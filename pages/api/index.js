let { PythonShell } = require('python-shell');
const app = require('express')();

app.get('/api', (req, res) => {
  let options = {
    mode: 'text',
    pythonOptions: ['-u'], // get print results in real-time
    scriptPath: './Python/Bloomberg',
    args: [req.query.fields, req.query.tickers, req.query.startdate, req.query.enddate, 'momentum'],
  };
  console.log(options)
  //res.setHeader('Cache-Control', 's-max-age=1, stale-while-revalidate');
  PythonShell.run('main_front.py', options).then((messages) => {
    // results is an array consisting of messages collected during execution
    //console.log('results: %j', messages);
    res.status(200);
    res.setHeader('Content-Type', 'application/json');
    res.json({ messages });
  });
});

module.exports = app;
