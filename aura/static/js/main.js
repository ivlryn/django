// main.js
$(document).ready(function() {
    $('#categoryTabs a').on('click', function(e) {
        e.preventDefault();
        
        // Update active tab
        $('#categoryTabs a').removeClass('active');
        $(this).addClass('active');

        const categoryId = $(this).data('category');

        // Show/hide products with fade animation
        if (categoryId === 'all') {
            $('.product-card').fadeIn(400);
        } else {
            $('.product-card').each(function() {
                if ($(this).data('category') == categoryId) {
                    $(this).fadeIn(400);
                } else {
                    $(this).fadeOut(400);
                }
            });
        }
    });
});

// AJAX Add to Cart
$(document).on('submit', '.add-to-cart-form', function(e) {
    e.preventDefault();  // Prevent page refresh/jump

    var $form = $(this);
    var $button = $form.find('.btn-add-cart');
    var $icon = $button.find('i');

    // Optional: Visual feedback (change icon briefly)
    $icon.removeClass('fa-plus').addClass('fa-check');

    $.ajax({
        type: 'POST',
        url: $form.attr('action'),
        data: $form.serialize(),
        success: function(response) {
            // Assume your cart_add view redirects or renders on success.
            // Since it's a session cart, we fetch the new count separately.

            // Simple way: Reload only the badge via AJAX from current page
            $.get(window.location.href, function(data) {
                var newCount = $(data).find('#cart-badge').text();
                $('#cart-badge').text(newCount);
            });

            // Alternative (better): Make cart_add view return JSON with count
            // (see step 3 below), then: $('#cart-badge').text(response.cart_count);

            // Reset icon after delay
            setTimeout(function() {
                $icon.removeClass('fa-check').addClass('fa-plus');
            }, 1000);

            // Optional: Show success toast/message if you have one
        },
        error: function() {
            alert('Error adding to cart. Please try again.');
            $icon.removeClass('fa-check').addClass('fa-plus');
        }
    });
});




