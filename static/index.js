$(function() {
    var vm = new Vue({
        el: '#middle',
        data: { user: null, requests: [], before: '9999-12-31T23:59:59.999999Z', query: '' },
        methods: {
            login: function() {
                var provider = new firebase.auth.GoogleAuthProvider();
                firebase.auth().signInWithRedirect(provider).catch(function(error) { alert(error.message); });
            },
            create: function() {
                firebase.auth().currentUser.getIdToken().then(function(userIdToken) {
                    $.ajax({ url: '/create_request', type: 'POST', headers: {'Authorization': 'Bearer ' + userIdToken}
                    }).always(function() { vm.requests = []; vm.before = '9999-12-31T23:59:59.999999Z'; fetch(); });
                });
            },
            search: function(query) {
                window.location.href = "/search?q="+query;
            },
            convert: function(contents) { return convert(contents) }
        }
    });
    firebase.auth().onAuthStateChanged(function(user) {
        if (user) {
            vm.user = true; 
            var fetching = false;
            window.onscroll = function() {
                if (window.innerHeight+window.scrollY > document.body.offsetHeight-500) { if (!fetching) { fetch(); fetching = true; } }
                else { fetching = false; }
            }
            fetch();
        } else { vm.user = false; }
    });
    function fetch() {
        firebase.auth().currentUser.getIdToken().then(function(userIdToken) {
            var data = {'before': vm.before, 'source': 'alive'};
            $.ajax({ url: '/fetch_requests', type: 'GET', headers: {'Authorization': 'Bearer ' + userIdToken}, data: data
            }).then(function(response) { vm.requests = vm.requests.concat(response); vm.before = vm.requests[vm.requests.length-1].created; });
        });
    }
});