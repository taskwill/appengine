$(function(){
    var vm = new Vue({
        el: '#middle',
        data: { user: false, request: null, mode: 'edit', payments: [], hour: null, twc: null, removed: false },
        methods: {
            edit: function() { vm.mode = 'save'; },
            save: function() { vm.mode = 'edit'; },
            edit: function(item_id) {
                vm.mode = 'save';
                $('.editor').css('display', 'none'); $('textarea').css('display', 'block'); var element = $('textarea')[0];
                element.style.height = '5px'; element.style.height = (element.scrollHeight)+'px'; //element.focus();
            },
            resize: function(event) {
                var element = event.target; element.style.height = '5px'; element.style.height = (element.scrollHeight)+'px';
            }, 
            save: function(item_id) {
                vm.mode = 'edit';
                var contents = $('textarea').val(); var data = {'request_id': vm.request.request_id, 'contents': contents};
                firebase.auth().currentUser.getIdToken().then(function(userIdToken) {
                    $.ajax({ url: '/update_request', type: 'POST', headers: {'Authorization': 'Bearer ' + userIdToken}, data: data });
                });
                $('textarea').css('display', 'none'); $('.editor').css('display', 'block');
            },
            remove: function(request_id) {
                firebase.auth().currentUser.getIdToken().then(function(userIdToken) {
                    $.ajax({ url: '/remove_request', type: 'POST', headers: {'Authorization': 'Bearer '+userIdToken}, data: {'request_id': request_id}
                    }).always(function() { vm.request.removed = true; });
                });
            },
            restore: function(request_id) {
                firebase.auth().currentUser.getIdToken().then(function(userIdToken) {
                    $.ajax({ url: '/restore_request', type: 'POST', headers: {'Authorization': 'Bearer ' + userIdToken}, data: {'request_id': request_id }
                    }).then(function() { vm.request.removed = false; })
                });
            },
            delete_forever: function(request_id) {
                firebase.auth().currentUser.getIdToken().then(function(userIdToken) {
                    $.ajax({ url: '/delete_request', type: 'POST', headers: {'Authorization': 'Bearer ' + userIdToken}, data: {'request_id': request_id}
                    }).always(function() { window.location.reload(); });
                });
            },
            ago: function(time) {
                var passed = Date.now() - new Date(time); var s = 1000; var m = 60*s; var h = 60*m; var d = 24*h; var y = 365.25*d;
                function f(x) { return Math.floor(passed/x); } if (f(y)) { return f(y) + 'y ago'; } else if (f(d)) { return f(d) + 'd ago'; }
                else if (f(h)) { return f(h) + 'h ago'; } else if (f(m)) { return f(m) + 'm ago'; } else { return 'Just now'; }
            },
            pay: function(request_id) {
                firebase.auth().currentUser.getIdToken().then(function(userIdToken) {
                    $.ajax({ url: '/fetch_payments', type: 'GET', headers: {'Authorization': 'Bearer ' + userIdToken}, data: {'request_id': request_id}
                    }).then(function(response) { vm.payments = response; });
                });
            },
            submit: function(request_id, twc, hour) {
                if (twc && hour) {
                    vm.twc = null; vm.hour = null;
                    firebase.auth().currentUser.getIdToken().then(function(userIdToken) {
                        $.ajax({
                            url: '/submit', type: 'POST', headers: {'Authorization': 'Bearer ' + userIdToken},
                            data: {'request_id': request_id, 'twc': twc, 'hour': hour}
                        }).always(function() { vm.pay(vm.request.request_id); });
                    });
                }
            },
            cancel: function(payment_id) {
                firebase.auth().currentUser.getIdToken().then(function(userIdToken) {
                    $.ajax({ url: '/cancel', type: 'POST', headers: {'Authorization': 'Bearer ' + userIdToken}, data: {'payment_id': payment_id}
                    }).always(function() { vm.pay(vm.request.request_id); });
                });
            },
            convert: function(contents) { return convert(contents) }
        }
    });
    
    firebase.auth().onAuthStateChanged(function(user) {
        if (user) {
            vm.user = true;
            var data = {'request_id': window.location.pathname.split('/')[2]};
            firebase.auth().currentUser.getIdToken().then(function(userIdToken) {
                $.ajax({ url: '/fetch_request', type: 'GET', headers: {'Authorization': 'Bearer ' + userIdToken}, data: data
                }).then(function(response) { vm.request = response; });
                $.ajax({ url: '/fetch_payments', type: 'GET', headers: {'Authorization': 'Bearer ' + userIdToken}, data: data
                }).then(function(response) { vm.payments = response; });
            });
        }
        else { location.replace("/"); }
    });
});