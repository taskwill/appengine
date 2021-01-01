$(function(){
    var vm = new Vue({
        el: '#middle',
        data: { user: false, pairs: [] },
        methods: {
            create: function() {
                firebase.auth().currentUser.getIdToken().then(function(userIdToken) {
                    $.ajax({ url: '/create_pair', type: 'POST', headers: {'Authorization': 'Bearer ' + userIdToken}
                    }).always(function() { fetch(); });
                });
            },
            select: function(pair_id, which) {
                firebase.auth().currentUser.getIdToken().then(function(userIdToken) {
                    var data = { 'which': which, 'pair_id': pair_id };
                    $.ajax({ url: '/update_pair', type: 'POST', headers: {'Authorization': 'Bearer ' + userIdToken}, data: data });
                });
            },
            convert: function(contents) { return convert(contents) }
        }
    });
    
    firebase.auth().onAuthStateChanged(function(user) {
        if (user) { vm.user = true; fetch(); }
        else { location.replace("/"); vm.auth = 'continue'; }
    });
    
    function fetch() {
        firebase.auth().currentUser.getIdToken().then(function(userIdToken) {
            $.ajax({ url: '/fetch_pairs', type: 'GET', headers: {'Authorization': 'Bearer ' + userIdToken}
            }).then(function(response) { vm.pairs = response; });
        });
    }
});