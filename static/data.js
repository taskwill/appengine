function download_data() {
    firebase.auth().currentUser.getIdToken().then(function(userIdToken) {
        $.ajax({ url: '/download_data', type: 'GET', headers: {'Authorization': 'Bearer ' + userIdToken} }).then(function(data) {
            var zip = JSZip(); zip.file('data/user_data.csv', data['user_data']); zip.file('data/request_data.csv', data['request_data']);
            zip.generateAsync({type:"blob"}).then(function (blob) { saveAs(blob, "data.zip"); });
        });
    });
}