$(function(){
    var vm = new Vue({
        el: '#middle',
        data: {},
        methods: {
            expand_delete_account: function() { $('#delete_details').slideToggle(100); },
            leave: function() {
                var user = firebase.auth().currentUser;
                user.getIdToken().then(function(userIdToken) {
                    var confirmed = confirm('Are you really sure you want to delete your account ('+user.email+')? You cannot undo it.');
                    if (confirmed) {
                        $.ajax({ url: '/delete_account', type: 'POST', headers: {'Authorization': 'Bearer ' + userIdToken} }).then(function(data) {
                            user.delete().then(function() { vm.auth = 'continue'
                            }).catch(function(error) { alert(error.message); });
                        });
                    }
                });
            }
        }
    });
});