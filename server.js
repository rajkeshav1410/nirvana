const express = require('express');
const path = require('path');
const app = express();
const { spawn } = require("child_process");
const port = 3000;

app.use('/', express.static(__dirname + '/'));
app.use('/webpage', express.static(__dirname + '/webpage'));

app.use(express.json());

app.get('/', function(req, res) {
    res.sendFile(__dirname + "/webpage/index.html");
});

app.post('/popularity', function(req, res) {
    const popout = spawn('python', ['./loader.py', 'popularity', req.query.n]);
    popout.stdout.on('data', function(data) {
        // console.log(data.toString());
        res.write(data);
        res.end();
    });
});

app.post('/next_song', function(req, res) {
    const { song_name } = req.body;
    console.log(song_name);
    const popout = spawn('python', ['./loader.py', 'collaborative', song_name]);
    popout.stdout.on('data', function(data) {
        // console.log(data.toString());
        res.write(data);
        res.end();
    });
});

app.post('/related_song', function(req, res) {
    const { song_name } = req.body;
    console.log(song_name);
    const popout = spawn('python', ['./loader.py', 'similarity', song_name]);
    popout.stdout.on('data', function(data) {
        // console.log(data.toString());
        res.write(data);
        res.end();
    });
});

app.post('/search', function(req, res) {
    const { song_name } = req.body;
    const popout = spawn('python', ['./loader.py', 'search', song_name]);
    popout.stdout.on('data', function(data) {
        // console.log(data.toString());
        res.write(data);
        res.end();
    });
});

app.get("/song_page", function(req, res) {
    res.sendFile(path.resolve('webpage/snippets/song_page.html'));
});

app.listen(port, () => console.log("Server is running on http://localhost:" + port));