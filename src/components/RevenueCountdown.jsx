import React, { useState, useEffect } from 'react';
import './RevenueCountdown.css';

const RevenueCountdown = () => {
  const [data, setData] = useState({
    currentArr: 0,
    targetArr: 1000000,
    targetDate: new Date('2024-12-31')
  });

  useEffect(() => {
    fetch('/api/metrics')
      .then(res => res.json())
      .then(data => {
        setData({
          currentArr: data.current_arr,
          targetArr: data.target_arr,
          targetDate: new Date(data.target_date)
        });
      });
  }, []);

  const [timeLeft, setTimeLeft] = useState(calculateTimeLeft());

  function calculateTimeLeft() {
    const now = new Date();
    const difference = data.targetDate - now;
    
    return {
      days: Math.floor(difference / (1000 * 60 * 60 * 24)),
      hours: Math.floor((difference / (1000 * 60 * 60)) % 24)
    };
  }

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeLeft(calculateTimeLeft());
    }, 3600000); // Update every hour

    return () => clearInterval(timer);
  }, []);

  const progressPercentage = (data.currentArr / data.targetArr) * 100;
  const monthsRemaining = timeLeft.days / 30;
  const revenueGap = data.targetArr - data.currentArr;
  const monthlyTarget = revenueGap / monthsRemaining;

  return (
    <div className="countdown-container">
      <h1>Road to £1M ARR</h1>
      
      <div className="metric-container">
        <div className="current-arr">
          <h2>Current ARR</h2>
          <div className="value">£{data.currentArr.toLocaleString()}</div>
        </div>

        <div className="time-remaining">
          <h2>Time Remaining</h2>
          <div className="value">{timeLeft.days}d {timeLeft.hours}h</div>
        </div>
      </div>

      <div className="metric-container">
        <div className="monthly-target">
          <h2>Monthly Target</h2>
          <div className="value">£{Math.round(monthlyTarget).toLocaleString()}</div>
        </div>
      </div>

      <div className="progress-section">
        <div className="progress-bar">
          <div 
            className="progress-fill"
            style={{ width: `${progressPercentage}%` }}
          />
        </div>
        <div className="remaining-amount">
          £{(data.targetArr - data.currentArr).toLocaleString()} to go
        </div>
      </div>
    </div>
  );
};

export default RevenueCountdown; 