$(function(){
    var vm = new Vue({
        el: '#middle',
        data: { requests: [], before: '9999-12-31T23:59:59.999999Z' },
        methods: { convert: function(contents) { return convert(contents) } }
    });
    
    firebase.auth().onAuthStateChanged(function(user) {
        if (user) { fetch(vm.mode); }
        else { firebase.auth().signInAnonymously().catch(function(error) { alert(error.message); }); }
    });
    
    function fetch() {
        firebase.auth().currentUser.getIdToken().then(function(userIdToken) {
            var data = { 'before': vm.before, 'source': 'trash' };
            $.ajax({ url: '/fetch_requests', type: 'GET', headers: {'Authorization': 'Bearer ' + userIdToken}, data: data
            }).then(function(response) { vm.requests = response; });
        });
    }
});