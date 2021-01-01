$(function(){
    var vm = new Vue({
        el: '#middle',
        data: { user: false },
        methods: { logout: function() { firebase.auth().signOut().then(function() { vm.auth = 'continue'; }).catch(function(error) { alert(error); }); } }
    });
    
    firebase.auth().onAuthStateChanged(function(user) { if (user) { vm.user = true; } else { location.replace("/"); } });
});