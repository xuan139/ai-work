"""Seed an idempotent manufacturing-company dataset from an Odoo shell.

Run with:
    odoo-bin shell -d <database> -c <config> --no-http \
        < tools/odoo/seed_manufacturing_company.py
"""

from __future__ import annotations

import json
import os
from datetime import date, datetime, timedelta


COMPANY_NAME = "Goldsys 智造示範股份有限公司"
COMPANY_KEY = "goldsys_manufacturing"
DEMO_MODULE = "ai_work_manufacturing_demo"


def find_xmlid(key):
    return env.ref(f"{DEMO_MODULE}.{key}", raise_if_not_found=False)


def bind_xmlid(key, record):
    existing = env["ir.model.data"].search(
        [("module", "=", DEMO_MODULE), ("name", "=", key)], limit=1
    )
    values = {"model": record._name, "res_id": record.id, "noupdate": True}
    if existing:
        existing.write(values)
    else:
        env["ir.model.data"].create({"module": DEMO_MODULE, "name": key, **values})
    return record


def upsert(key, model, values):
    record = find_xmlid(key)
    if record and record._name == model and record.exists():
        record.write(values)
        return record
    return bind_xmlid(key, env[model].create(values))


def scoped(model):
    return env[model].with_company(company).with_context(
        allowed_company_ids=list(set(env.user.company_ids.ids + [company.id])),
        force_company=company.id,
    )


def product(key, code, name, category, cost, price, uom):
    values = {
        "name": name,
        "default_code": code,
        "categ_id": category.id,
        "uom_id": uom.id,
        "purchase_ok": True,
        "sale_ok": True,
        "is_storable": True,
        "standard_price": cost,
        "list_price": price,
        "company_id": company.id,
    }
    template = upsert(key, "product.template", values)
    return template.product_variant_id


def partner(key, ref, name, *, supplier=False, customer=False, **extra):
    values = {
        "name": name,
        "ref": ref,
        "is_company": True,
        "company_id": company.id,
        "supplier_rank": 1 if supplier else 0,
        "customer_rank": 1 if customer else 0,
        **extra,
    }
    return upsert(key, "res.partner", values)


def bom(key, code, finished_product, quantity, components):
    values = {
        "code": code,
        "product_tmpl_id": finished_product.product_tmpl_id.id,
        "product_id": finished_product.id,
        "product_qty": quantity,
        "product_uom_id": finished_product.uom_id.id,
        "type": "normal",
        "company_id": company.id,
        "bom_line_ids": [(5, 0, 0)]
        + [
            (
                0,
                0,
                {
                    "product_id": component.id,
                    "product_qty": component_qty,
                    "product_uom_id": component.uom_id.id,
                    "company_id": company.id,
                },
            )
            for component, component_qty in components
        ],
    }
    return upsert(key, "mrp.bom", values)


def supplier_price(key, vendor, item, price, minimum=1, delay=7):
    return upsert(
        key,
        "product.supplierinfo",
        {
            "partner_id": vendor.id,
            "product_tmpl_id": item.product_tmpl_id.id,
            "price": price,
            "min_qty": minimum,
            "delay": delay,
            "currency_id": company.currency_id.id,
            "company_id": company.id,
        },
    )


def purchase_order(key, vendor, reference, lines, *, confirm=False, days_ago=0):
    order = find_xmlid(key)
    if not order:
        order = bind_xmlid(
            key,
            scoped("purchase.order").create(
                {
                    "partner_id": vendor.id,
                    "partner_ref": reference,
                    "company_id": company.id,
                    "currency_id": company.currency_id.id,
                    "date_order": datetime.now() - timedelta(days=days_ago),
                    "order_line": [
                        (
                            0,
                            0,
                            {
                                "product_id": item.id,
                                "name": item.display_name,
                                "product_qty": quantity,
                                "product_uom_id": item.uom_id.id,
                                "price_unit": price,
                                "date_planned": datetime.now() + timedelta(days=7),
                            },
                        )
                        for item, quantity, price in lines
                    ],
                }
            ),
        )
    if confirm and order.state in {"draft", "sent"}:
        order.button_confirm()
    return order


def sale_order(key, customer, reference, lines, *, confirm=False, days_ago=0):
    order = find_xmlid(key)
    if not order:
        order = bind_xmlid(
            key,
            scoped("sale.order").create(
                {
                    "partner_id": customer.id,
                    "client_order_ref": reference,
                    "company_id": company.id,
                    "warehouse_id": warehouse.id,
                    "date_order": datetime.now() - timedelta(days=days_ago),
                    "order_line": [
                        (
                            0,
                            0,
                            {
                                "product_id": item.id,
                                "name": item.display_name,
                                "product_uom_qty": quantity,
                                "product_uom_id": item.uom_id.id,
                                "price_unit": price,
                            },
                        )
                        for item, quantity, price in lines
                    ],
                }
            ),
        )
    if confirm and order.state in {"draft", "sent"}:
        order.action_confirm()
    return order


def manufacturing_order(key, origin, item, quantity, item_bom, *, confirm=False):
    order = find_xmlid(key)
    if not order:
        picking_type = scoped("stock.picking.type").search(
            [("code", "=", "mrp_operation"), ("warehouse_id", "=", warehouse.id)],
            limit=1,
        )
        order = bind_xmlid(
            key,
            scoped("mrp.production").create(
                {
                    "origin": origin,
                    "product_id": item.id,
                    "product_qty": quantity,
                    "product_uom_id": item.uom_id.id,
                    "bom_id": item_bom.id,
                    "company_id": company.id,
                    "picking_type_id": picking_type.id,
                    "location_src_id": warehouse.lot_stock_id.id,
                    "location_dest_id": warehouse.lot_stock_id.id,
                    "date_start": datetime.now() + timedelta(days=2),
                }
            ),
        )
    if confirm and order.state == "draft":
        order.action_confirm()
    return order


def invoice(key, partner_record, move_type, reference, lines, *, post=False, days_ago=0):
    move = find_xmlid(key)
    if not move:
        move = bind_xmlid(
            key,
            scoped("account.move").create(
                {
                    "move_type": move_type,
                    "partner_id": partner_record.id,
                    "company_id": company.id,
                    "currency_id": company.currency_id.id,
                    "invoice_date": date.today() - timedelta(days=days_ago),
                    "ref": reference,
                    "invoice_line_ids": [
                        (
                            0,
                            0,
                            {
                                "product_id": item.id,
                                "name": item.display_name,
                                "quantity": quantity,
                                "product_uom_id": item.uom_id.id,
                                "price_unit": price,
                            },
                        )
                        for item, quantity, price in lines
                    ],
                }
            ),
        )
    if post and move.state == "draft":
        move.action_post()
    return move


required_modules = {
    "account",
    "hr",
    "hr_holidays",
    "l10n_tw",
    "mrp",
    "mrp_account",
    "purchase",
    "purchase_stock",
    "sale_management",
    "sale_stock",
    "stock",
    "stock_account",
}
installed = set(
    env["ir.module.module"].search(
        [("name", "in", sorted(required_modules)), ("state", "=", "installed")]
    ).mapped("name")
)
missing = sorted(required_modules - installed)
if missing:
    raise RuntimeError(f"Required Odoo modules are not installed: {', '.join(missing)}")

tw = env.ref("base.tw")
twd = env.ref("base.TWD")
company = find_xmlid(COMPANY_KEY)
company_values = {
    "name": COMPANY_NAME,
    "country_id": tw.id,
    "currency_id": twd.id,
    "street": "台北市內湖區瑞光路 100 號",
    "city": "台北市",
    "zip": "114",
    "phone": "+886-2-2658-8800",
    "email": "demo@goldsys.io",
    "website": "https://goldsys.io",
}
if company:
    company.write(company_values)
else:
    company = bind_xmlid(COMPANY_KEY, env["res.company"].create(company_values))

administrators = env.user | env.ref("base.user_admin")
for administrator in administrators:
    if company not in administrator.company_ids:
        administrator.write({"company_ids": [(4, company.id)]})

company_env = env(context={
    **env.context,
    "allowed_company_ids": list(set(env.user.company_ids.ids + [company.id])),
    "force_company": company.id,
})
env = company_env
company = env["res.company"].browse(company.id)

if not scoped("account.account").search_count([("company_ids", "in", company.id)]):
    env["account.chart.template"].try_loading("tw", company=company, install_demo=False)

warehouse = scoped("stock.warehouse").search([("company_id", "=", company.id)], limit=1)
if not warehouse:
    warehouse = scoped("stock.warehouse").create(
        {"name": "台北智慧工廠", "code": "GSF", "company_id": company.id}
    )
else:
    warehouse.write({"name": "台北智慧工廠", "code": "GSF"})

unit = env.ref("uom.product_uom_unit")
kg = env.ref("uom.product_uom_kgm")

categories = {
    "raw": upsert("category_raw", "product.category", {"name": "DEMO / 原物料"}),
    "semi": upsert("category_semi", "product.category", {"name": "DEMO / 半成品"}),
    "finished": upsert("category_finished", "product.category", {"name": "DEMO / 成品"}),
    "packaging": upsert("category_packaging", "product.category", {"name": "DEMO / 包材"}),
}

products = {
    "aluminum": product("product_aluminum", "RM-AL6061", "6061 鋁板", categories["raw"], 135, 180, kg),
    "steel": product("product_steel", "RM-SS304", "304 不鏽鋼材", categories["raw"], 95, 130, kg),
    "pcb": product("product_pcb", "RM-PCB-CTRL", "工控主板", categories["raw"], 3200, 4200, unit),
    "motor": product("product_motor", "RM-MOTOR-400", "400W 伺服馬達", categories["raw"], 4800, 6200, unit),
    "sensor": product("product_sensor", "RM-SENSOR-PROX", "近接感測器", categories["raw"], 650, 900, unit),
    "bolt": product("product_bolt", "RM-BOLT-M6", "M6 不鏽鋼螺栓", categories["raw"], 4, 8, unit),
    "cable": product("product_cable", "RM-CABLE-SET", "控制線組", categories["raw"], 420, 650, unit),
    "paint": product("product_paint", "RM-PAINT-BLUE", "工業藍烤漆", categories["raw"], 260, 360, unit),
    "carton": product("product_carton", "PKG-CARTON-L", "大型強化紙箱", categories["packaging"], 120, 180, unit),
    "control_box": product("product_control_box", "SA-CONTROL-BOX", "智慧控制箱", categories["semi"], 5200, 7800, unit),
    "drive_module": product("product_drive_module", "SA-DRIVE-MODULE", "輸送驅動模組", categories["semi"], 6100, 8900, unit),
    "conveyor": product("product_conveyor", "FG-SMART-CONVEYOR", "智慧輸送機 SC-100", categories["finished"], 42000, 68000, unit),
    "inspection": product("product_inspection", "FG-VISION-STATION", "AI 視覺檢測站 VI-200", categories["finished"], 58000, 96000, unit),
}

vendors = {
    "metal": partner("vendor_metal", "V-DEMO-001", "台灣精密鋼材股份有限公司", supplier=True, email="sales@tw-metal.example", phone="02-2799-1100", street="新北市五股區五工路 88 號", city="新北市"),
    "electronics": partner("vendor_electronics", "V-DEMO-002", "福爾摩沙電子元件有限公司", supplier=True, email="service@formosa-components.example", phone="03-577-2200", street="新竹市科學園區一路 16 號", city="新竹市"),
    "motion": partner("vendor_motion", "V-DEMO-003", "亞太傳動科技有限公司", supplier=True, email="order@apex-motion.example", phone="04-2359-3300", street="台中市工業區三路 28 號", city="台中市"),
    "packaging": partner("vendor_packaging", "V-DEMO-004", "永續包裝企業社", supplier=True, email="sales@green-pack.example", phone="06-253-4400", street="台南市永康區中正路 168 號", city="台南市"),
}
customers = {
    "automation": partner("customer_automation", "C-DEMO-001", "新光自動化股份有限公司", customer=True, email="purchase@shinkong-auto.example", phone="02-2500-5100", street="台北市松山區南京東路 300 號", city="台北市"),
    "logistics": partner("customer_logistics", "C-DEMO-002", "亞洲智慧物流有限公司", customer=True, email="procurement@asia-logistics.example", phone="03-398-6200", street="桃園市大園區航勤北路 12 號", city="桃園市"),
    "robotics": partner("customer_robotics", "C-DEMO-003", "太平洋機器人系統股份有限公司", customer=True, email="buyer@pacific-robotics.example", phone="07-811-7300", street="高雄市前鎮區成功二路 25 號", city="高雄市"),
}

supplier_price("price_aluminum", vendors["metal"], products["aluminum"], 135, 100, 10)
supplier_price("price_steel", vendors["metal"], products["steel"], 95, 100, 10)
supplier_price("price_pcb", vendors["electronics"], products["pcb"], 3200, 10, 14)
supplier_price("price_sensor", vendors["electronics"], products["sensor"], 650, 20, 7)
supplier_price("price_motor", vendors["motion"], products["motor"], 4800, 5, 12)
supplier_price("price_carton", vendors["packaging"], products["carton"], 120, 50, 5)

boms = {
    "control_box": bom("bom_control_box", "BOM-SA-CB-001", products["control_box"], 1, [(products["pcb"], 1), (products["sensor"], 2), (products["cable"], 1), (products["bolt"], 8)]),
    "drive_module": bom("bom_drive_module", "BOM-SA-DM-001", products["drive_module"], 1, [(products["motor"], 1), (products["cable"], 1), (products["bolt"], 8)]),
}
boms["conveyor"] = bom("bom_conveyor", "BOM-FG-SC100-001", products["conveyor"], 1, [(products["aluminum"], 25), (products["steel"], 10), (products["control_box"], 1), (products["drive_module"], 2), (products["bolt"], 40), (products["paint"], 3), (products["carton"], 1)])
boms["inspection"] = bom("bom_inspection", "BOM-FG-VI200-001", products["inspection"], 1, [(products["aluminum"], 15), (products["control_box"], 1), (products["sensor"], 4), (products["cable"], 2), (products["bolt"], 24), (products["carton"], 1)])

opening_quantities = {
    "aluminum": 1500,
    "steel": 900,
    "pcb": 80,
    "motor": 60,
    "sensor": 240,
    "bolt": 5000,
    "cable": 300,
    "paint": 120,
    "carton": 200,
    "control_box": 12,
    "drive_module": 16,
    "conveyor": 5,
    "inspection": 3,
}
for product_key, target_quantity in opening_quantities.items():
    item = products[product_key]
    quant = scoped("stock.quant").search(
        [("product_id", "=", item.id), ("location_id", "=", warehouse.lot_stock_id.id)],
        limit=1,
    )
    current_quantity = quant.quantity if quant else 0
    difference = target_quantity - current_quantity
    if difference:
        scoped("stock.quant")._update_available_quantity(
            item, warehouse.lot_stock_id, difference
        )

purchase_orders = [
    purchase_order("po_confirmed_metal", vendors["metal"], "DEMO-PO-METAL-001", [(products["aluminum"], 500, 132), (products["steel"], 300, 92)], confirm=True, days_ago=12),
    purchase_order("po_draft_electronics", vendors["electronics"], "DEMO-PO-ELEC-002", [(products["pcb"], 30, 3150), (products["sensor"], 100, 640)], days_ago=2),
]

sale_orders = [
    sale_order("so_confirmed_conveyor", customers["automation"], "DEMO-SO-SC100-001", [(products["conveyor"], 4, 68000)], confirm=True, days_ago=8),
    sale_order("so_draft_inspection", customers["logistics"], "DEMO-QUO-VI200-002", [(products["inspection"], 2, 96000)], days_ago=1),
    sale_order("so_confirmed_mix", customers["robotics"], "DEMO-SO-MIX-003", [(products["conveyor"], 2, 66000), (products["inspection"], 1, 93000)], confirm=True, days_ago=5),
]

manufacturing_orders = [
    manufacturing_order("mo_confirmed_conveyor", "DEMO-MO-SC100-001", products["conveyor"], 6, boms["conveyor"], confirm=True),
    manufacturing_order("mo_draft_inspection", "DEMO-MO-VI200-002", products["inspection"], 3, boms["inspection"]),
]

departments = {}
for key, name in (
    ("management", "經營管理部"),
    ("sales", "業務部"),
    ("procurement", "採購部"),
    ("manufacturing", "製造部"),
    ("quality", "品質工程部"),
    ("warehouse", "倉儲物流部"),
    ("finance", "財務部"),
):
    departments[key] = upsert(
        f"department_{key}",
        "hr.department",
        {"name": name, "company_id": company.id},
    )

employees = (
    ("general_manager", "陳志明", "總經理", "management", "gm@goldsys-demo.example"),
    ("sales_manager", "林雅雯", "業務經理", "sales", "sales.manager@goldsys-demo.example"),
    ("sales_specialist", "王柏凱", "業務專員", "sales", "sales01@goldsys-demo.example"),
    ("buyer", "張淑芬", "採購專員", "procurement", "buyer@goldsys-demo.example"),
    ("production_manager", "黃俊傑", "製造經理", "manufacturing", "production@goldsys-demo.example"),
    ("production_engineer", "周冠宇", "製程工程師", "manufacturing", "pe@goldsys-demo.example"),
    ("technician", "李承翰", "組裝技術員", "manufacturing", "tech01@goldsys-demo.example"),
    ("quality_engineer", "蔡佩珊", "品質工程師", "quality", "qa@goldsys-demo.example"),
    ("warehouse_keeper", "鄭文豪", "倉管專員", "warehouse", "warehouse@goldsys-demo.example"),
    ("accountant", "許佳玲", "會計專員", "finance", "accounting@goldsys-demo.example"),
)
for key, name, job_title, department_key, email in employees:
    upsert(
        f"employee_{key}",
        "hr.employee",
        {
            "name": name,
            "job_title": job_title,
            "department_id": departments[department_key].id,
            "work_email": email,
            "company_id": company.id,
        },
    )

invoices = [
    invoice("invoice_customer_posted", customers["automation"], "out_invoice", "DEMO-INV-2026-001", [(products["conveyor"], 2, 68000)], post=True, days_ago=15),
    invoice("invoice_customer_draft", customers["robotics"], "out_invoice", "DEMO-INV-2026-002", [(products["inspection"], 1, 96000)], days_ago=1),
    invoice("bill_vendor_posted", vendors["electronics"], "in_invoice", "DEMO-BILL-ELEC-001", [(products["pcb"], 10, 3200), (products["sensor"], 20, 650)], post=True, days_ago=18),
]

summary = {
    "company": {"id": company.id, "name": company.name},
    "warehouse": {"id": warehouse.id, "name": warehouse.name, "code": warehouse.code},
    "counts": {
        "departments": len(departments),
        "employees": len(employees),
        "vendors": len(vendors),
        "customers": len(customers),
        "products": len(products),
        "boms": len(boms),
        "purchase_orders": len(purchase_orders),
        "sale_orders": len(sale_orders),
        "manufacturing_orders": len(manufacturing_orders),
        "invoices_and_bills": len(invoices),
    },
}

if os.getenv("ODOO_DEMO_DRY_RUN") == "1":
    env.cr.rollback()
    summary["committed"] = False
else:
    env.cr.commit()
    summary["committed"] = True

print("AI_WORK_ODOO_DEMO_RESULT=" + json.dumps(summary, ensure_ascii=False, sort_keys=True))
