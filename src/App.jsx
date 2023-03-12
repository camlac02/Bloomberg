import { useState } from 'react'
import Chart from './Components/chart'
import image from './assets/image.png'
import './App.css'

function App() {
  return (
    <div className="App">
      <div>

      <img className="h-auto max-w-full" src={image} alt="image description"/>
      {Chart()}
      </div>
      
    </div>
  )
}

export default App
