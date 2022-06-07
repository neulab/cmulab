import logo from './logo.svg';
import './App.css';
import React, {useState} from 'react';
import axios from 'axios';

axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'



function App() {

  const [file, setFile] = useState()
  const [text, setText] = useState()

  function handleChange(event) {
    setFile(event.target.files[0])
  }

  function handleSubmit(event) {
    event.preventDefault()
    const url = 'http://localhost:8088/annotator/ocr-post-correction/';
    //const url = '/annotator/ocr-post-correction/';
    const formData = new FormData();
    formData.append('file', file);
    formData.append('fileName', file.name);
    const config = {
      headers: {
        'content-type': 'multipart/form-data',
        'Authorization': '8470ede027588b80c5b82ab5c9e78b8daea68635'
      },
    };
    axios.post(url, formData, config).then((response) => {
      console.log(response.data);
      setText(response.data)
    });

  }

  return (
    <div className="App">
      <form onSubmit={handleSubmit}>
        <h1>Upload image or pdf</h1>
        <input type="file" onChange={handleChange}/>
        <button type="submit">Upload</button>
        <div>
          {JSON.stringify(text, null, 2)}
        </div>
      </form>
    </div>
  );
}

export default App;
