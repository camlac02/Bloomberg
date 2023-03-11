import React, { useState } from 'react';
import useSWR from 'swr';
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
  
  const fetcher = (...args) => fetch(...args).then((res) => res.json());

  ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
  );

 const options = {
responsive: true,
plugins: {
    legend: {
    position: 'top',
    },
    title: {
    display: true,
    text: 'Close prices',
    },
},
};

const Chart = (data) => {

 if (data) {
  const finalData = data.data
  console.log(finalData)
  console.log(finalData?.messages[0])
  const APIfinalDataJsonClose = JSON.parse(finalData?.messages[0])
  const APIfinalDataJsonDd = JSON.parse(finalData?.messages[1])
  const APIfinalDataJsonMdd = JSON.parse(finalData?.messages[2])
  const APIfinalDataListValues = JSON.parse(finalData?.messages[3])
  console.log(APIfinalDataJsonClose)

  const finalDataJsonClose = {
      labels: APIfinalDataJsonClose.map((data) => data.ts),
      datasets: [
        {
          label: 'Close Prices',
          data: APIfinalDataJsonClose.map((data) => data.close),
          borderColor: 'rgb(53, 162, 235)',
          backgroundColor: 'rgba(53, 162, 235, 0.5)',
        }
      ],
    };
    const finalDataJsonDd = {
      labels: APIfinalDataJsonDd.map((data) => data.ts),
      datasets: [
        {
          label: 'Drawdown',
          data: APIfinalDataJsonDd.map((data) => data.drawdown),
          borderColor: 'rgb(53, 162, 235)',
          backgroundColor: 'rgba(53, 162, 235, 0.5)',
        }
      ],
    };
    const finalDataJsonMdd = {
      labels: APIfinalDataJsonMdd.map((data) => data.ts),
      datasets: [
        {
          label: 'Drawdown',
          data: APIfinalDataJsonMdd.map((data) => data.mdd),
          borderColor: 'rgb(53, 162, 235)',
          backgroundColor: 'rgba(53, 162, 235, 0.5)',
        },
        {
          label: 'Maximum Drawdown',
          data: APIfinalDataJsonDd.map((data) => data.drawdown),
          borderColor: 'rgb(255, 0, 0)',
          backgroundColor: 'rgba(255, 0, 0, 0.5)',
        }
      ],
    };

    return (<div className="flex flex-col my-2">
    <div><Line options={options} data={finalDataJsonClose}/></div>
    <div><Line options={options} data={finalDataJsonDd}/></div>
    <div><Line options={options} data={finalDataJsonMdd}/></div>
  </div>
    )
      }
    }
export default Chart