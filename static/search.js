$(function(){
    var vm = new Vue({
        el: '#middle',
        data: { user: false, requests: [] },
        methods: {
            search_requests: function(query) {
                firebase.auth().currentUser.getIdToken().then(function(userIdToken) {
                    $.ajax({ url: '/search_requests', type: 'GET', headers: {'Authorization': 'Bearer ' + userIdToken}, data: {'query': query}
                    }).then(function(response) { vm.requests = response; });
                });
            },
            convert: function(contents) { return convert(contents) }
        }
    });
    
    firebase.auth().onAuthStateChanged(function(user) {
        if (user) { vm.user = true; vm.search_requests(new URLSearchParams(window.location.search).get('q')) }
        else { location.replace("/"); }
    });
});