import React, { useState } from 'react';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
  } from 'chart.js';
  import { Line } from 'react-chartjs-2';
import jsondata from "./MDDMomentum.json"

  ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
  );

export const options = {
responsive: true,
plugins: {
    legend: {
    position: 'top',
    },
    title: {
    display: true,
    text: 'MaximumDrawdown Momentum',
    },
},
};

const Chart = () => {
  const [data, setData] = useState();

  const finalData = {
    labels: jsondata.map((data) => data.ts),
    datasets: [
      {
        label: 'MDDMomentum',
        data: jsondata.map((data) => data.close),
        borderColor: 'rgb(53, 162, 235)',
        backgroundColor: 'rgba(53, 162, 235, 0.5)',
      }
    ],
  };
  

    return (<><button onClick={() => handleReadString2()}>readString</button><Line options={options} data={finalData}/></>)
    
    }
export default Chart