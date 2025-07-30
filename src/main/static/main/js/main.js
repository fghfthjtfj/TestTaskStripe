var cartBuyBtn = document.getElementById('cart-buy');
cartBuyBtn.addEventListener('click', function() {
  handleBuyClick('/buy/');
});


var itemBuyBtn = document.getElementById('item-buy');
var itemId = itemBuyBtn.getAttribute('data-item-id');
itemBuyBtn.addEventListener('click', function() {
  handleBuyClick('/buy/' + itemId + '/');
});


function handleBuyClick(url) {
  fetch(url, {method: 'GET'})
    .then(response => response.json())
    .then(data => {
      if (data.status === 'success' && data.id && data.key) {
        var stripe = Stripe(data.key);
        stripe.redirectToCheckout({ sessionId: data.id });
      } else {
        alert(data.error);
      }
    })
    .catch(function(e) {
      console.log(e); // ошибка пустой корзины не обработана так как UI весьма упрощённый
    });
}
