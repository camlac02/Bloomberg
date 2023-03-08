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

const Chart = (chart) => {

console.log(chart.chart.fields)
const fields = chart.chart.fields
const tickers = chart.chart.tickers
const startDate = chart.chart.startDate
const endDate = chart.chart.endDate

   const { data, error, isLoading } = useSWR(`/api?fields=${fields}&tickers=${tickers}&startdate=${startDate}&enddate=${endDate}`, fetcher);
  
   if (error) return <div>Failed to load</div>;
   if (isLoading) return <div>
  <div

      >Loading...
  </div>
 </div>
 ;

 if (data) {
  console.log(data)
  const API = JSON.parse(data?.messages[0])

  const finalData = {
      labels: API.map((data) => data.ts),
      datasets: [
        {
          label: 'BacktesterMomentum',
          data: API.map((data) => data.close),
          borderColor: 'rgb(53, 162, 235)',
          backgroundColor: 'rgba(53, 162, 235, 0.5)',
        }
      ],
    };

    return (<Line options={options} data={finalData}/>)
      }
    }
export default Chart