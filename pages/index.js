import { useState, useEffect } from "react";
import useSWR from "swr";
import Head from "next/head";
import Image from "next/image";
import { Inter } from "next/font/google";
import styles from "@/styles/Home.module.css";
import Chart from "../components/chart";
import Table from "../components/table";
import { registerLocale, setDefaultLocale } from "react-datepicker";
import { TailSpin } from "react-loader-spinner";
import DatePicker from "react-datepicker";
import fr from "date-fns/locale/fr";
import moment from "moment";
import "react-datepicker/dist/react-datepicker.css";

registerLocale("fr", fr);
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Line } from "react-chartjs-2";

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
  const [message, setMessage] = useState("");
  const [shouldFetch, setShouldFetch] = useState(false);

  const [chart, setChart] = useState({
    fields: "",
    tickers: "",
    startDate: "",
    endDate: "",
    strategies: "",
    optimisation: "",
    rebalancement: "",
    generic: "",
    options: "",
    frais: "",
  });

  const { data, error, mutate, isLoading } = useSWR(
    shouldFetch
      ? `/api?fields=${chart.fields}&tickers=${
          chart.tickers
        }&startdate=${moment(chart.startDate).format()}&enddate=${moment(
          chart.endDate
        ).format()}&strategies=${chart.strategies}&optimisation=${
          chart.optimisation
        }&rebalancement=${chart.rebalancement}&generic=${
          chart.generic
        }&options=${chart.options}&frais=${chart.frais}`
      : null,
    fetcher
  );

  const triggerPython = () => {
    setShouldFetch(true);
    mutate();
  };

  const handleSubmit = (event) => {
    // prevents the submit button from refreshing the page
    event.preventDefault();
  };

  return (
    <>
      <Head>
        <meta name="description" content="Generated by create next app" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <main>
        <div className="flex flex-row">
          <div className="basis-32" />
          <div className="basis-full">
            <div className="text-center">
              <h1 className="text-4xl font-bold tracking-tight text-gray-300 sm:text-6xl my-4">
                BLOOMBERG
              </h1>
              <p className="mt-6 text-lg leading-8 text-gray-500">
                Data retrieval & applications
              </p>
            </div>
            <div className="mx-auto max-w-xl">
              <form onSubmit={handleSubmit} className="space-y-5">
                <div className="grid grid-cols-12 gap-5">
                  <div className="col-span-12">
                    <label
                      htmlFor="example9"
                      className="mb-1 block text-sm font-medium text-gray-500 after:ml-0.5 after:text-red-500 after:content-['*']"
                    >
                      Fields
                    </label>
                    <input
                      type="text"
                      id="example9"
                      required
                      className="block h-8 w-full rounded-md border-gray-300 shadow-sm focus:border-primary-400 focus:ring focus:ring-primary-200 focus:ring-opacity-50 disabled:cursor-not-allowed disabled:bg-gray-50 disabled:text-gray-500"
                      placeholder="PX_LAST"
                      value={chart.fields}
                      onChange={(e) =>
                        setChart({ ...chart, fields: e.target.value })
                      }
                    />
                  </div>
                  <div className="col-span-12">
                    <label
                      htmlFor="example9"
                      className="mb-1 block text-sm font-medium text-gray-500 after:ml-0.5 after:text-red-500 after:content-['*']"
                    >
                      Tickers
                    </label>
                    <input
                      type="text"
                      id="example9"
                      className="block h-8 w-full rounded-md border-gray-300 shadow-sm focus:border-primary-400 focus:ring focus:ring-primary-200 focus:ring-opacity-50 disabled:cursor-not-allowed disabled:bg-gray-50 disabled:text-gray-500"
                      placeholder="CAC Index"
                      value={chart.tickers}
                      onChange={(e) =>
                        setChart({ ...chart, tickers: e.target.value })
                      }
                    />
                  </div>
                  <div className="col-span-6">
                    <label
                      htmlFor="example7"
                      className="mb-1 block text-sm font-medium text-gray-500 after:ml-0.5 after:text-red-500 after:content-['*']"
                    >
                      Date de début
                    </label>
                    <DatePicker
                      showIcon
                      dateFormat="dd-MM-yyyy"
                      locale="fr"
                      selected={chart.startDate}
                      maxDate={
                        new Date(new Date().setDate(new Date().getDate() - 3))
                      }
                      onChange={(date) =>
                        setChart({ ...chart, startDate: date })
                      }
                      className="block h-8 w-full rounded-md border-gray-300 shadow-sm focus:border-primary-400 focus:ring focus:ring-primary-200 focus:ring-opacity-50 disabled:cursor-not-allowed disabled:bg-gray-50 disabled:text-gray-500"
                    />
                  </div>
                  <div className="col-span-6">
                    <label
                      htmlFor="example8"
                      className="mb-1 block text-sm font-medium text-gray-500 after:ml-0.5 after:text-red-500 after:content-['*']"
                    >
                      Date de fin
                    </label>
                    <DatePicker
                      showIcon
                      dateFormat="dd-MM-yyyy"
                      locale="fr"
                      selected={chart.endDate}
                      maxDate={
                        new Date(new Date().setDate(new Date().getDate() - 2))
                      }
                      onChange={(date) => setChart({ ...chart, endDate: date })}
                      className="block h-8 w-full rounded-md border-gray-300 shadow-sm focus:border-primary-400 focus:ring focus:ring-primary-200 focus:ring-opacity-50 disabled:cursor-not-allowed disabled:bg-gray-50 disabled:text-gray-500"
                    />
                  </div>
                  <div className="col-span-6">
                    <label
                      htmlFor="example3"
                      className="mb-1 block text-sm font-medium text-gray-500 after:ml-0.5 after:text-red-500 after:content-['*']"
                    >
                      Stratégie
                    </label>
                    <select
                      id="example3"
                      className="block w-full h-8 rounded-md border-gray-300 shadow-sm focus:border-primary-300 focus:ring focus:ring-primary-200 focus:ring-opacity-50 disabled:cursor-not-allowed disabled:bg-gray-50"
                      onChange={(e) =>
                        setChart({ ...chart, strategies: e.target.value })
                      }
                    >
                      <option value="">Sélectionner une stratégie</option>
                      <option value="btm">Book-to-Market</option>
                      <option value="mc">Market Capitalization</option>
                      <option value="momentum">Momentum</option>
                    </select>
                  </div>

                  <div className="col-span-6">
                    <label
                      htmlFor="example3"
                      className="mb-1 block text-sm font-medium text-gray-500 after:ml-0.5 after:text-red-500 after:content-['*']"
                    >
                      Optimisation
                    </label>
                    <select
                      id="example3"
                      className="block w-full h-8 rounded-md border-gray-300 shadow-sm focus:border-primary-300 focus:ring focus:ring-primary-200 focus:ring-opacity-50 disabled:cursor-not-allowed disabled:bg-gray-50"
                      onChange={(e) =>
                        setChart({ ...chart, optimisation: e.target.value })
                      }
                    >
                      <option value="">Sélectionner une optimisation</option>
                      <option value="max_sharpe">Maximisation Sharpe</option>
                      <option value="min_variance">
                        Minimisation Variance
                      </option>
                      <option value="risk_parity">Risk Parity</option>
                    </select>
                  </div>

                  <div className="col-span-6">
                    <label
                      htmlFor="example9"
                      className="mb-1 block text-sm font-medium text-gray-500"
                    >
                      Rebalancement
                    </label>
                    <input
                      type="text"
                      id="example9"
                      className="block h-8 w-full rounded-md border-gray-300 shadow-sm focus:border-primary-400 focus:ring focus:ring-primary-200 focus:ring-opacity-50 disabled:cursor-not-allowed disabled:bg-gray-50 disabled:text-gray-500"
                      placeholder="10"
                      value={chart.rebalancement}
                      onChange={(e) =>
                        setChart({ ...chart, rebalancement: e.target.value })
                      }
                    />
                  </div>

                  <div className="col-span-6">
                    <label
                      htmlFor="example3"
                      className="mb-1 block text-sm font-medium text-gray-500"
                    >
                      Données génériques
                    </label>
                    <select
                      id="example3"
                      className="block w-full h-8 rounded-md border-gray-300 shadow-sm focus:border-primary-300 focus:ring focus:ring-primary-200 focus:ring-opacity-50 disabled:cursor-not-allowed disabled:bg-gray-50"
                      onChange={(e) =>
                        setChart({ ...chart, generic: e.target.value })
                      }
                    >
                      <option value="">Sélectionner un type de data</option>
                      <option value="True">Génériques</option>
                      <option value="False">Non génériques</option>
                    </select>
                  </div>

                  <div className="col-span-6">
                    <label
                      htmlFor="example9"
                      className="mb-1 block text-sm font-medium text-gray-500"
                    >
                      Options
                    </label>
                    <input
                      type="text"
                      id="example9"
                      className="block h-8 w-full rounded-md border-gray-300 shadow-sm focus:border-primary-400 focus:ring focus:ring-primary-200 focus:ring-opacity-50 disabled:cursor-not-allowed disabled:bg-gray-50 disabled:text-gray-500"
                      placeholder="LAG1, LAG2, Other_data"
                      value={chart.options}
                      onChange={(e) =>
                        setChart({ ...chart, options: e.target.value })
                      }
                    />
                  </div>

                  <div className="col-span-6">
                    <label
                      htmlFor="example9"
                      className="mb-1 block text-sm font-medium text-gray-500"
                    >
                      Trading Cost
                    </label>
                    <input
                      type="text"
                      id="example9"
                      className="block h-8 w-full rounded-md border-gray-300 shadow-sm focus:border-primary-400 focus:ring focus:ring-primary-200 focus:ring-opacity-50 disabled:cursor-not-allowed disabled:bg-gray-50 disabled:text-gray-500"
                      placeholder="0.0002"
                      value={chart.frais}
                      onChange={(e) =>
                        setChart({ ...chart, frais: e.target.value })
                      }
                    />
                  </div>
                </div>

                <div className="col-span-12 text-center py-14">
                  {chart.fields == "" ||
                  chart.tickers == "" ||
                  chart.startDate == "" ||
                  chart.endDate == "" ||
                  chart.strategies == "" ||
                  chart.optimisation == "" ? (
                    <>
                      <button
                        type="button"
                        disabled
                        className="rounded-lg border border-gray-700 bg-gray-700 px-5 py-2.5 text-center text-sm font-medium text-white shadow-sm transition-all hover:border-gray-900 hover:bg-gray-900 focus:ring focus:ring-gray-200 disabled:cursor-not-allowed disabled:border-gray-300 disabled:bg-gray-300"
                      >
                        VALIDER
                      </button>
                      <p className="mt-4 text-red-500">
                        Tous les champs* sont obligatoires
                      </p>
                    </>
                  ) : (
                    <button
                      onClick={triggerPython}
                      type="button"
                      disabled={isLoading}
                      className="rounded-lg border border-gray-700 bg-gray-700 px-5 py-2.5 text-center text-sm font-medium text-white shadow-sm transition-all hover:border-gray-900 hover:bg-gray-900 focus:ring focus:ring-gray-200 disabled:cursor-not-allowed disabled:border-gray-300 disabled:bg-gray-300"
                    >
                      VALIDER
                    </button>
                  )}
                </div>
              </form>
            </div>

            {data ? (
              <>
                <Chart data={data} />
                <Table data={data} />
              </>
            ) : isLoading ? (
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
                />
              </div>
            ) : (
              ""
            )}
          </div>
          <div className="basis-32" />
        </div>
      </main>
    </>
  );
}