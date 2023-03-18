const Table = (data) => {
  const finalData = data.data;
  const APIfinalDataListValues = JSON.parse(finalData?.messages[3]);
  console.log(finalData);
  console.log(APIfinalDataListValues);
  return (
    <div>
      <table className="w-full border-collapse bg-white text-left text-sm text-gray-500">
        <thead className="bg-gray-50">
          <tr>
            <th scope="col" className="px-6 py-4 font-medium text-gray-900">
              Indicateurs de risque
            </th>
            <th scope="col" className="px-6 py-4 font-medium text-gray-900">
              Valeurs
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100 border-t border-gray-100">
          {APIfinalDataListValues.map((data) => (
            <tr>
              <th className="px-6 py-4 font-medium text-gray-900">
                {data.variable}
              </th>
              <td className="px-6 py-4">{data.value}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
export default Table;
