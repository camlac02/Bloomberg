import { useState, useEffect } from 'react';
import useSWR from 'swr';
import Head from 'next/head';
import Image from 'next/image';
import { Inter } from 'next/font/google';
import styles from '@/styles/Home.module.css';
import Chart from '../components/chart';
import  { registerLocale, setDefaultLocale } from "react-datepicker";
import { TailSpin } from  'react-loader-spinner'
import DatePicker from "react-datepicker"
import fr from 'date-fns/locale/fr';
import moment from "moment";
import "react-datepicker/dist/react-datepicker.css";

registerLocale('fr', fr)
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

export default function Home() {
  const [message, setMessage] = useState('');
  const [shouldFetch, setShouldFetch] = useState(false);

  const [chart, setChart] = useState({
    fields: "",
    tickers: "",
    startDate: "",
    endDate: "",
    strategies: ""
  });

  const [finalChart, setFinalChart] = useState(false);
  const { data, error, mutate, isLoading } = useSWR(shouldFetch ? `/api?fields=${chart.fields}&tickers=${chart.tickers}&startdate=${moment(chart.startDate).format()}&enddate=${moment(chart.endDate).format()}&strategies=${chart.strategies}`: null, fetcher);

  const triggerPython = () => {
    setShouldFetch(true)
    mutate()
}

  const handleChange = (event) => {
    setChart({ ...chart, [event.target.name]: event.target.value });
  };

  const handleSubmit = (event) => {
    // prevents the submit button from refreshing the page
    event.preventDefault();
   
  };
  const handleClick = () => {
    setFinalChart(true)
  };

  const options = {
    responsive: true,
    plugins: {
        legend: {
        position: 'top',
        },
        title: {
        display: true,
        text: 'Chart.js Line Chart',
        },
    },
    };


  return (
    <>
      <Head>
        <meta name='description' content='Generated by create next app' />
        <meta name='viewport' content='width=device-width, initial-scale=1' />
        <link rel='icon' href='/favicon.ico' />
      </Head>
      <main>
      <div className="flex flex-row">
  <div className="basis-32"/>
  <div className="basis-full">
  <div className="text-center">
          <h1 className="text-4xl font-bold tracking-tight text-gray-300 sm:text-6xl my-4">BLOOMBERG</h1>
          <p className="mt-6 text-lg leading-8 text-gray-500">Data retrieval & applications</p>
        </div>
<div className="mx-auto max-w-xl">
  <form onSubmit={handleSubmit} className="space-y-5">
    <div className="grid grid-cols-12 gap-5">
      <div className="col-span-12">
        <label htmlFor="example9" className="mb-1 block text-sm font-medium text-gray-500">Fields</label>
        <input type="text" id="example9" className="block h-8 w-full rounded-md border-gray-300 shadow-sm focus:border-primary-400 focus:ring focus:ring-primary-200 focus:ring-opacity-50 disabled:cursor-not-allowed disabled:bg-gray-50 disabled:text-gray-500" placeholder="PX_LAST" value={chart.fields} onChange={(e) => setChart({...chart, fields: e.target.value})} />
      </div>
      <div className="col-span-12">
        <label htmlFor="example9" className="mb-1 block text-sm font-medium text-gray-500">Tickers</label>
        <input type="text" id="example9" className="block h-8 w-full rounded-md border-gray-300 shadow-sm focus:border-primary-400 focus:ring focus:ring-primary-200 focus:ring-opacity-50 disabled:cursor-not-allowed disabled:bg-gray-50 disabled:text-gray-500" placeholder="CAC Index" value={chart.tickers} onChange={(e) => setChart({...chart, tickers: e.target.value})}/>
      </div>
      <div className="col-span-6">
        <label htmlFor="example7" className="mb-1 block text-sm font-medium text-gray-500">Date de début</label>
        <DatePicker
      showIcon
      dateFormat="dd-MM-yyyy"
      locale="fr"
      selected={chart.startDate}
      onChange={(date) => setChart({...chart, startDate: date})}
      className="block h-8 w-full rounded-md border-gray-300 shadow-sm focus:border-primary-400 focus:ring focus:ring-primary-200 focus:ring-opacity-50 disabled:cursor-not-allowed disabled:bg-gray-50 disabled:text-gray-500"
    />
      </div>
      <div className="col-span-6">
        <label htmlFor="example8" className="mb-1 block text-sm font-medium text-gray-500">Date de fin</label>
        <DatePicker
      showIcon
      dateFormat="dd-MM-yyyy"
      locale="fr"
      selected={chart.endDate}
      onChange={(date) => setChart({...chart, endDate: date})}
    
      className="block h-8 w-full rounded-md border-gray-300 shadow-sm focus:border-primary-400 focus:ring focus:ring-primary-200 focus:ring-opacity-50 disabled:cursor-not-allowed disabled:bg-gray-50 disabled:text-gray-500"
    />
      </div>
    <div className="col-span-12 mb-4">
      <div className="mx-auto max-w-xs">
        <label htmlFor="example3" className="mb-1 block text-sm font-medium text-gray-500">Stratégie</label>
  <select id="example3" className="block w-full h-8 rounded-md border-gray-300 shadow-sm focus:border-primary-300 focus:ring focus:ring-primary-200 focus:ring-opacity-50 disabled:cursor-not-allowed disabled:bg-gray-50"
  onChange={(e) => setChart({...chart, strategies: e.target.value})}
  >
    <option value="btm">Book-to-Market</option>
    <option value="mc">Market Capitalization</option>
    <option value="momentum">Momentum</option>
  </select>
</div>
</div>
      <div className="col-span-12 text-center my-6">
        <button onClick={triggerPython} type="button" className="rounded-lg border border-primary-500 bg-primary-500 px-5 py-2.5 text-center text-sm font-medium shadow-sm transition-all hover:border-primary-700 hover:bg-primary-700 focus:ring focus:ring-primary-200 disabled:cursor-not-allowed disabled:border-primary-300 disabled:bg-primary-300">VALIDER</button>
      </div>
    </div>
  </form>
</div>

{data ?<Chart data={data} />: isLoading ? 
<div className="flex justify-center my-9">
  <TailSpin
  height="80"
  width="80"
  color="#3287a8"
  ariaLabel="tail-spin-loading"
  radius="1"
  wrapperStyle={{}}
  wrapperClass=""
  visible={true}
/></div> : "" 
}
  
</div>
<div className="basis-32"/>
    </div>
  </main>
    </>
  );
}
