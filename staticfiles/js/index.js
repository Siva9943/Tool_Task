console.log("hello siva")
document.addEventListener('DOMContentLoaded', function () {
    var forms = document.querySelectorAll('.product-update-form');
    console.log(forms)
    forms.forEach(function (form) {
        form.addEventListener('submit', function (e) {
            e.preventDefault()
            var isValid = true;

            function clearError(input) {
                input.classList.remove('is-invalid');
                var feedback = input.parentElement.querySelector('.invalid-feedback');
                if (feedback) feedback.textContent = '';
            }

            function showError(input, message) {
                isValid = false;
                input.classList.add('is-invalid');
                var feedback = input.parentElement.querySelector('.invalid-feedback');
                if (feedback) feedback.textContent = message;
            }

            var code = form.querySelector('[name="product_code"]');
            var name = form.querySelector('[name="product_name"]');
            var desc = form.querySelector('[name="description"]');
            var category = form.querySelector('[name="item_category"]');
            var cost = form.querySelector('[name="cost_price"]');
            var selling = form.querySelector('[name="selling_price"]');
            var qty = form.querySelector('[name="quantity"]');

            [code, name, desc, category, cost, selling, qty].forEach(clearError);

    
            var codeVal = code.value.trim();
            if (!codeVal) {
                showError(code, 'Product Code is required.');
            } else if (!/^P\d+$/.test(codeVal)) {
                showError(code, 'Product Code must be like P001.');
            } else if (codeVal.length > 20) {
                showError(code, 'Product Code cannot exceed 20 characters.');
            }

            
            var nameVal = name.value.trim();
            if (!nameVal) {
                showError(name, 'Product Name is required.');
            } else if (nameVal.length > 40) {
                showError(name, 'Product Name cannot exceed 40 characters.');
            } else if (!/[A-Za-z]/.test(nameVal)) {
                showError(name, 'Product Name must contain letters, not just numbers.');
            }

    
            var descVal = desc.value.trim();
            if (!descVal) {
                showError(desc, 'Description is required.');
            } else if (!/[A-Za-z]/.test(descVal)) {
                showError(desc, 'Description must contain letters, not just numbers.');
            }

        
            var categoryVal = category.value.trim();
            if (!categoryVal) {
                showError(category, 'Item Category is required.');
            }
            else if (categoryVal.length > 20) {
                showError(category, 'Item Category cannot exceed 20 characters.');
            }
            else if (!/[A-Za-z]/.test(categoryVal)) {
                showError(category, 'Item Category must contain letters.');
            }

        
            var costVal = parseFloat(cost.value);
            if (cost.value.trim() === '' || isNaN(costVal)) {
                showError(cost, 'Cost Price must be numeric.');
            } else if (costVal < 0) {
                showError(cost, 'Cost Price cannot be negative.');
            }

            
            var sellingVal = parseFloat(selling.value);
            if (selling.value.trim() === '' || isNaN(sellingVal)) {
                showError(selling, 'Selling Price must be numeric.');
            } else if (sellingVal < 0) {
                showError(selling, 'Selling Price cannot be negative.');
            } else if (!isNaN(costVal) && sellingVal < costVal) {
                showError(selling, 'Selling Price must be greater than or equal to Cost Price.');
            }

        
            var qtyVal = qty.value.trim();
            if (qtyVal === '' || !/^-?\d+$/.test(qtyVal)) {
                showError(qty, 'Quantity must be an integer.');
            } else if (parseInt(qtyVal, 10) < 0) {
                showError(qty, 'Quantity cannot be negative.');
            }

              if (isValid) {
                form.submit(); 
            }
            
        });
    });
});


// toast


