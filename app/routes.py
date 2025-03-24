from flask import render_template, request, jsonify
from app import app, db
from app.models import Product, Sale
import os  # Add this line
from flask import Response
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
from flask import Response
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch


# Homepage Route
@app.route("/")
def index():
    return render_template("index.html")

# Add a new product
@app.route("/add_product", methods=["POST"])
def add_product():
    data = request.json
    name = data.get("name")
    price_per_kg = data.get("price_per_kg")

    if not name or not price_per_kg:
        return jsonify({"error": "Invalid data"}), 400

    new_product = Product(name=name, price_per_kg=price_per_kg)
    db.session.add(new_product)
    db.session.commit()

    return jsonify({"message": "Product added successfully"}), 201

# Get all products
@app.route("/get_products", methods=["GET"])
def get_products():
    products = Product.query.all()
    product_list = [{"id": p.id, "name": p.name, "price_per_kg": p.price_per_kg} for p in products]
    return jsonify(product_list)

# Process a sale
@app.route("/create_sale", methods=["POST"])
def create_sale():
    data = request.json
    print("Received Sale Data:", data)  # Debugging
    product_id = data.get("product_id")
    weight_kg = data.get("weight_kg")

    product = Product.query.get(product_id)
    if not product:
        print("❌ Product not found!")  # Debugging
        return jsonify({"error": "Product not found"}), 404

    total_price = round(product.price_per_kg * weight_kg, 2)
    new_sale = Sale(product_id=product_id, weight_kg=weight_kg, total_price=total_price)
    db.session.add(new_sale)
    db.session.commit()
    
    print("✅ Sale Recorded:", new_sale.id)  # Debugging
    return jsonify({"message": "Sale recorded", "total_price": total_price})


# Get all sales
@app.route("/get_sales", methods=["GET"])
def get_sales():
    sales = Sale.query.order_by(Sale.date.desc()).all()  # Order by latest date first
    sale_list = [
        {
            "id": s.id,
            "product_name": s.product.name,
            "weight_kg": s.weight_kg,
            "total_price": s.total_price,
            "date": s.date.strftime("%Y-%m-%d %H:%M:%S")
        }
        for s in sales
    ]
    return jsonify(sale_list)



@app.route("/generate_invoice/<int:sale_id>")
def generate_invoice(sale_id):
    sale = Sale.query.get(sale_id)
    if not sale:
        return jsonify({"error": "Sale not found"}), 404

    product = Product.query.get(sale.product_id)

    # Create a PDF file in memory
    pdf_buffer = io.BytesIO()
    pdf = canvas.Canvas(pdf_buffer, pagesize=letter)
    pdf.setTitle(f"Invoice_{sale.id}")

    # Invoice Title
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(200, 750, "Chicken Shop Invoice")

    # Sale Details
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, 700, f"Invoice ID: {sale.id}")
    pdf.drawString(50, 680, f"Date: {sale.date.strftime('%Y-%m-%d %H:%M:%S')}")
    pdf.drawString(50, 650, f"Product: {product.name}")
    pdf.drawString(50, 630, f"Weight: {sale.weight_kg} Kg")
    pdf.drawString(50, 610, f"Price per Kg: ₹{product.price_per_kg}")
    pdf.drawString(50, 590, f"Total Amount: ₹{sale.total_price}")

    # Footer
    pdf.setFont("Helvetica-Oblique", 10)
    pdf.drawString(50, 550, "Thank you for your purchase!")

    # Save PDF in memory and return as response
    pdf.save()
    pdf_buffer.seek(0)

    return Response(pdf_buffer, mimetype="application/pdf", headers={"Content-Disposition": f"attachment;filename=invoice_{sale.id}.pdf"})

