document.addEventListener("DOMContentLoaded", () => {
    loadProducts();
    loadSales();
});

// Function to add a product
function addProduct() {
    let name = document.getElementById("productName").value;
    let price = document.getElementById("productPrice").value;

    fetch("/add_product", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: name, price_per_kg: parseFloat(price) })
    }).then(response => response.json())
      .then(data => {
          alert(data.message);
          loadProducts();
      });
}

// Function to load products into the dropdown
function loadProducts() {
    fetch("/get_products")
    .then(response => response.json())
    .then(products => {
        let productSelect = document.getElementById("productSelect");
        productSelect.innerHTML = "";
        products.forEach(product => {
            let option = document.createElement("option");
            option.value = product.id;
            option.textContent = `${product.name} - ₹${product.price_per_kg}/kg`;
            productSelect.appendChild(option);
        });
    });
}

// ✅ Function to create a sale (Fixed API endpoint & JSON keys)
function createSale() {
    let productId = document.getElementById("productSelect").value;
    let weightKg = document.getElementById("weight").value;

    console.log("Creating Sale with:", { productId, weightKg }); // Debugging

    fetch("/create_sale", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ product_id: parseInt(productId), weight_kg: parseFloat(weightKg) })
    })
    .then(response => response.json())
    .then(data => {
        console.log("Server Response:", data);  // Debugging
        alert(`Sale recorded! Total Price: ₹${data.total_price}`);
        loadSales();
    })
    .catch(error => console.error("❌ Error:", error));
}


// ✅ Function to load sales history (Ensures new sales appear)
// Function to load sales history with grouping by date
function loadSales() {
    fetch("/get_sales")
    .then(response => response.json())
    .then(sales => {
        let salesTableBody = document.getElementById("salesTableBody");
        salesTableBody.innerHTML = "";

        let lastDate = ""; // Track the last date to group sales

        sales.forEach(sale => {
            let saleDate = sale.date.split(" ")[0]; // Extract only the date part (YYYY-MM-DD)

            // If a new date appears, insert a date header row
            if (saleDate !== lastDate) {
                let dateRow = `<tr class="sales-date-group"><td colspan="5">${saleDate}</td></tr>`;
                salesTableBody.innerHTML += dateRow;
                lastDate = saleDate; // Update the last seen date
            }

            // Insert sale details
            let row = `<tr>
                <td>${sale.product_name}</td>
                <td>${sale.weight_kg} Kg</td>
                <td>₹${sale.total_price}</td>
                <td>${sale.date}</td>
                <td><button class="invoice-btn" onclick="downloadInvoice(${sale.id})">Download</button></td>
            </tr>`;

            salesTableBody.innerHTML += row;
        });
    });
}


// ✅ Function to download invoice
function downloadInvoice(saleId) {
    window.open(`/generate_invoice/${saleId}`, "_blank");
}
