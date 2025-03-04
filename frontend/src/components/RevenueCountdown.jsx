import React, { useEffect, useState } from 'react';

const RevenueCountdown = () => {
  const [data, setData] = useState({
    currentArr: 0,
    targetArr: 0,
    targetDate: new Date()
  });

  useEffect(() => {
    fetch(`${process.env.REACT_APP_API_URL}/api/metrics`)
      .then(res => res.json())
      .then(data => {
        setData({
          currentArr: data.current_arr,
          targetArr: data.target_arr,
          targetDate: new Date(data.target_date)
        });
      });
  }, []);

  return (
    <div>
      {/* Render your component content here */}
    </div>
  );
};

export default RevenueCountdown; 