
document.getElementById("updateForm").addEventListener("submit", function(e) {
    const p_code=document.getElementById('p_code')
    const p_cat=document.getElementById('p_cat')
    const p_name=document.getElementById('p_name')
    const costPrice = parseFloat(document.getElementById("cost_price").value);
    const sellingPrice = parseFloat(document.getElementById("selling_price").value);
    const quantity = parseInt(document.getElementById("quantity").value);

    if(!p_code.startsWith('P')){
        alert("Product code Must Start with -P-")
        e.preventDefault()
        return;
    }
    if(isNaN(p_cat)){
        alert("There Category Must BE Character")
    }
    if (isNaN(costPrice) || costPrice <= 0) {
        alert("Cost Price must be greater than 0.");
        e.preventDefault();
        return;
    }

    if (isNaN(sellingPrice) || sellingPrice <= 0) {
        alert("Selling Price must be greater than 0.");
        e.preventDefault();
        return;
    }

    if (sellingPrice < costPrice) {
        alert("Selling Price cannot be less than Cost Price.");
        e.preventDefault();
        return;
    }

    if (isNaN(quantity) || quantity < 0) {
        alert("Quantity must be 0 or greater.");
        e.preventDefault();
        return;
    }

});