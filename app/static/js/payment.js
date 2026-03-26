document.addEventListener('DOMContentLoaded', function() {
    const countrySelect = document.getElementById('country');
    const gstRow = document.getElementById('gstRow');
    const totalAmount = document.getElementById('totalAmount');
    const paymentAmountInput = document.getElementById('payment_amount');
    const isNzAddressInput = document.getElementById('is_nz_address');
    
    const planPrice = parseFloat(document.getElementById('plan_price').value);
    const planGstPercentage = parseFloat(document.getElementById('plan_gst_percentage').value);

    function updateGstDisplay() {
        const selectedCountry = countrySelect.value;
        const isNZ = selectedCountry === 'NZ';
        
        if (isNzAddressInput) {
            isNzAddressInput.value = isNZ.toString();
        }
        
        if (gstRow) {
            if (isNZ) {
                gstRow.style.display = 'flex';
                gstRow.removeAttribute('hidden');
                gstRow.classList.remove('d-none');
            } else {
                gstRow.style.display = 'none';
                gstRow.setAttribute('hidden', 'hidden');
                gstRow.classList.add('d-none');
            }
        }
        
        let totalPrice;
        if (isNZ) {
            totalPrice = planPrice * (1 + planGstPercentage / 100);
        } else {
            totalPrice = planPrice;
        }
        
        if (totalAmount) {
            totalAmount.textContent = '$' + totalPrice.toFixed(2);
        }
        
        if (paymentAmountInput) {
            paymentAmountInput.value = totalPrice.toFixed(2);
        }
    }

    if (countrySelect) {
        countrySelect.addEventListener('change', updateGstDisplay);
        
        if (countrySelect.value) {
            updateGstDisplay();
        }
    }
    
    const cardNumberInput = document.getElementById('cardNumber');
    console.log("cardNumberInput" + cardNumberInput);
    if (cardNumberInput) {
        cardNumberInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            
            if (value.length > 0) {
                value = value.match(/.{1,4}/g).join('-');
            }
            
            if (value.length > 19) {
                value = value.substr(0, 19);
            }
            
            e.target.value = value;
        });
        
        // Validate Credit Card Number
        cardNumberInput.addEventListener('blur', function() {
            const rawNumber = this.value.replace(/-/g, '');
            if (rawNumber.length !== 16 || !/^\d{16}$/.test(rawNumber)) {
                this.classList.add('is-invalid');
            } else {
                this.classList.remove('is-invalid');
            }
        });
    }

    // Validate Expiry Date
    const expiryInput = document.querySelector('input[name="cardExpiryDate"]');
    if (expiryInput) {
        expiryInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length >= 2) {
                value = value.slice(0,2) + '/' + value.slice(2,6);
            }
            e.target.value = value;
            validateExpiryDate(this);
        });
    }
    
    // Validate expiry date
    function validateExpiryDate(input) {
        const value = input.value;
        const today = new Date();
        const currentMonth = today.getMonth() + 1; // Months are 0-indexed
        const currentYear = today.getFullYear();

        if (!/^\d{2}\/\d{4}$/.test(value)) {
            input.classList.add('is-invalid');
            input.setCustomValidity('Please enter date in MM/YYYY format');
            return;
        }

        const [month, year] = value.split('/').map(Number);

        if (month < 1 || month > 12) {
            input.classList.add('is-invalid');
            input.setCustomValidity('Invalid month');
            return;
        }

        if (year < currentYear || (year === currentYear && month < currentMonth)) {
            input.classList.add('is-invalid');
            input.setCustomValidity('Card has expired');
            return;
        }

        input.classList.remove('is-invalid');
        input.setCustomValidity('');
    }
});