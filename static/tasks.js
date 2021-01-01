$(function(){
    var vm = new Vue({
        el: '#middle',
        data: { user: false, tasks: [] },
        methods: {
            create: function() {
                firebase.auth().currentUser.getIdToken().then(function(userIdToken) {
                    $.ajax({ url: '/create_task', type: 'POST', headers: {'Authorization': 'Bearer ' + userIdToken}
                    }).always(function() { fetch(); });
                });
            },
            edit: function(item_id) {
                $('#'+item_id+'>.editor').css('display', 'none');
                $('#'+item_id+'>textarea').css('display', 'block');
                var element = $('#'+item_id+'>textarea')[0];
                element.style.height = '5px'; element.style.height = (element.scrollHeight)+'px'; element.focus();
                $('#'+item_id+'>button').css('display', 'block');
            },
            resize: function(event) {
                var element = event.target; element.style.height = '5px'; element.style.height = (element.scrollHeight)+'px';
            }, 
            update: function(item_id) {
                var contents = $('#'+item_id+'>textarea').val(); var data = {'item_id': item_id, 'contents': contents};
                firebase.auth().currentUser.getIdToken().then(function(userIdToken) {
                    $.ajax({ url: '/update_task', type: 'POST', headers: {'Authorization': 'Bearer ' + userIdToken}, data: data });
                });
                $('#'+item_id+'>textarea').css('display', 'none'); $('#'+item_id+'>button').css('display', 'none');
                $('#'+item_id+'>.editor').css('display', 'block');
            },
            convert: function(contents) { return convert(contents) }
        }
    });
    
    firebase.auth().onAuthStateChanged(function(user) {
        if (user) { vm.user = true; fetch(); } else { location.replace("/"); }
    });
    
    function fetch() {
        firebase.auth().currentUser.getIdToken().then(function(userIdToken) {
            $.ajax({ url: '/fetch_tasks', type: 'GET', headers: {'Authorization': 'Bearer ' + userIdToken}
            }).then(function(response) { vm.tasks = response; });
        });
    }
});