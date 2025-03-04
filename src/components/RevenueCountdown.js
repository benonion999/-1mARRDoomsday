import React, { useState, useEffect } from 'react';
import './RevenueCountdown.css';

function RevenueCountdown() {
  const [timeLeft, setTimeLeft] = useState({
    days: 0,
    hours: 0,
    minutes: 0,
    seconds: 0
  });

  const targetARR = 1000000; // £1M ARR
  const currentARR = 0; // You can update this with your current ARR
  const targetDate = new Date('2025-12-31'); // Set your target date here

  useEffect(() => {
    const timer = setInterval(() => {
      const now = new Date();
      const difference = targetDate - now;

      const days = Math.floor(difference / (1000 * 60 * 60 * 24));
      const hours = Math.floor((difference / (1000 * 60 * 60)) % 24);
      const minutes = Math.floor((difference / 1000 / 60) % 60);
      const seconds = Math.floor((difference / 1000) % 60);

      setTimeLeft({ days, hours, minutes, seconds });
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const progressPercentage = (currentARR / targetARR) * 100;

  return (
    <div className="countdown-container">
      <div className="doomsday-container">
        <h1>Road to £1M ARR</h1>
        <div className="progress-bar">
          <div 
            className="progress-fill"
            style={{ width: `${progressPercentage}%` }}
          ></div>
          <span className="progress-text">
            £{currentARR.toLocaleString()} / £{targetARR.toLocaleString()}
          </span>
        </div>
        <div className="countdown">
          <div className="time-block">
            <span className="number">{timeLeft.days}</span>
            <span className="label">Days</span>
          </div>
          <div className="time-block">
            <span className="number">{timeLeft.hours}</span>
            <span className="label">Hours</span>
          </div>
          <div className="time-block">
            <span className="number">{timeLeft.minutes}</span>
            <span className="label">Minutes</span>
          </div>
          <div className="time-block">
            <span className="number">{timeLeft.seconds}</span>
            <span className="label">Seconds</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default RevenueCountdown; 