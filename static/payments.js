$(function(){
    var vm = new Vue({
        el: '#middle',
        data: { amount: null }
    });
    
    paypal.Buttons({
        createOrder: function(data, actions) {
          return actions.order.create({
              purchase_units: [{ amount: { value: vm.amount } }]
          });
        },
        onApprove: function(data, actions) {
          return actions.order.capture().then(function(details) {
            return fetch('/pay_usd', {
                method: 'post', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ orderID: data.orderID })
            });
          });
        }
    }).render('#paypal');
});