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
    console.log(event.target.files)
    console.log(Array.from(event.target.files))
    //setFile(event.target.files[0])
    setFile(Array.from(event.target.files))
  }

  function handleSubmit(event) {
    event.preventDefault()
    //const url = 'http://localhost:8088/annotator/ocr-post-correction/';
    const url = 'http://rabat.sp.cs.cmu.edu:8088/annotator/ocr-post-correction/';
    //const url = '/annotator/ocr-post-correction/';
    const formData = new FormData();
    file.forEach(f=>{
        formData.append('file', f);
    });
    //formData.append('file', file);
    //formData.append('fileName', file.name);
    formData.append('params', '{"debug": 1}')
    formData.append('fileids', '{"filename1": "fileid1", "filename2": "fileid2"}')
    const config = {
      headers: {
        'content-type': 'multipart/form-data',
        //'Authorization': '8470ede027588b80c5b82ab5c9e78b8daea68635'
        'Authorization': '5e72d818c2f4250687f090bb7ec5466184982edc'
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
        <input type="file" multiple onChange={handleChange}/>
        <button type="submit">Upload</button>
        <div>
          {JSON.stringify(text, null, 2)}
        </div>
      </form>
    </div>
  );
}

export default App;
