import React, { useState } from "react";
import moment from "moment";
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

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const options1 = {
  responsive: true,
  plugins: {
    legend: {
      position: "top",
    },
    title: {
      display: true,
      text: "Close prices",
    },
  },
};

const options2 = {
  responsive: true,
  plugins: {
    legend: {
      position: "top",
    },
    title: {
      display: true,
      text: "Drawdown",
    },
  },
};

const options3 = {
  responsive: true,
  plugins: {
    legend: {
      position: "top",
    },
    title: {
      display: true,
      text: "Maximum Drawdown",
    },
  },
};

const Chart = (data) => {
  if (data) {
    const finalData = data.data;
    console.log(finalData);
    console.log(finalData?.messages[0]);
    const APIfinalDataJsonClose = JSON.parse(finalData?.messages[0]);
    const APIfinalDataJsonDd = JSON.parse(finalData?.messages[1]);
    const APIfinalDataJsonMdd = JSON.parse(finalData?.messages[2]);
    console.log(APIfinalDataJsonClose);

    const finalDataJsonClose = {
      labels: APIfinalDataJsonClose.map((data) =>
        moment(data.ts).format("MMM YY")
      ),
      datasets: [
        {
          label: "Close Prices",
          data: APIfinalDataJsonClose.map((data) => data.close),
          borderColor: "rgb(53, 162, 235)",
          backgroundColor: "rgba(53, 162, 235, 0.5)",
        },
      ],
    };
    const finalDataJsonDd = {
      labels: APIfinalDataJsonDd.map((data) =>
        moment(data.ts).format("MMM YY")
      ),
      datasets: [
        {
          label: "Drawdown",
          data: APIfinalDataJsonDd.map((data) => data.drawdown),
          borderColor: "rgb(53, 162, 235)",
          backgroundColor: "rgba(53, 162, 235, 0.5)",
        },
      ],
    };
    const finalDataJsonMdd = {
      labels: APIfinalDataJsonMdd.map((data) =>
        moment(data.ts).format("MMM YY")
      ),
      datasets: [
        {
          label: "Drawdown",
          data: APIfinalDataJsonDd.map((data) => data.drawdown),
          borderColor: "rgb(53, 162, 235)",
          backgroundColor: "rgba(53, 162, 235, 0.5)",
        },
        {
          label: "Maximum Drawdown",
          data: APIfinalDataJsonMdd.map((data) => data.mdd),
          borderColor: "rgb(255, 0, 0)",
          backgroundColor: "rgba(255, 0, 0, 0.5)",
        },
      ],
    };

    return (
      <div className="flex flex-col my-2">
        <div>
          <Line options={options1} data={finalDataJsonClose} />
        </div>
        <div>
          <Line options={options2} data={finalDataJsonDd} />
        </div>
        <div>
          <Line options={options3} data={finalDataJsonMdd} />
        </div>
      </div>
    );
  }
};
export default Chart;
