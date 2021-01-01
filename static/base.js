$(function(){
    var config = {
        apiKey: "",
        authDomain: "taskwill.firebaseapp.com",
        databaseURL: "https://taskwill.firebaseio.com",
        projectId: "taskwill",
        storageBucket: "taskwill.appspot.com",
        messagingSenderId: "",
        appId: ""
    };
    
    firebase.initializeApp(config);
});

function convert(contents) {
    // ![alt text](dropbox?raw=1 or GDrive/uc?id=id) Create the link converter.
    if (contents) {
        var contents = contents.replace('((key))', '?ref=campaign').replace('((key))', '?ref=campaign');
        var converter = new showdown.Converter(); return converter.makeHtml(contents);
    }
}