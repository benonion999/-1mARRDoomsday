class RevenueCountdown {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.data = {
            currentArr: 0,
            targetArr: 1000000,
            targetDate: new Date('2025-12-31')
        };
        this.init();
    }

    async init() {
        await this.fetchData();
        this.render();
        this.startTimer();
    }

    async fetchData() {
        try {
            const response = await fetch('/api/metrics');
            const data = await response.json();
            this.data = {
                currentArr: data.current_arr,
                targetArr: data.target_arr,
                targetDate: new Date(data.target_date)
            };
        } catch (error) {
            console.error('Error fetching metrics:', error);
        }
    }

    calculateTimeLeft() {
        const now = new Date();
        const difference = this.data.targetDate - now;
        
        return {
            days: Math.floor(difference / (1000 * 60 * 60 * 24)),
            hours: Math.floor((difference / (1000 * 60 * 60)) % 24)
        };
    }

    render() {
        const timeLeft = this.calculateTimeLeft();
        const progressPercentage = (this.data.currentArr / this.data.targetArr) * 100;
        const monthsRemaining = timeLeft.days / 30;
        const revenueGap = this.data.targetArr - this.data.currentArr;
        const monthlyTarget = revenueGap / monthsRemaining;

        this.container.innerHTML = `
            <div class="countdown-container">
                <h1>Road to £1M ARR</h1>
                
                <div class="metric-container">
                    <div class="current-arr">
                        <h2>Current ARR</h2>
                        <div class="value">£${this.data.currentArr.toLocaleString()}</div>
                    </div>

                    <div class="time-remaining">
                        <h2>Time Remaining</h2>
                        <div class="value">${timeLeft.days}d ${timeLeft.hours}h</div>
                    </div>
                </div>

                <div class="metric-container">
                    <div class="monthly-target">
                        <h2>Monthly Target</h2>
                        <div class="value">£${Math.round(monthlyTarget).toLocaleString()}</div>
                    </div>
                </div>

                <div class="progress-section">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${progressPercentage}%"></div>
                    </div>
                    <div class="remaining-amount">
                        £${(this.data.targetArr - this.data.currentArr).toLocaleString()} to go
                    </div>
                </div>
            </div>
        `;
    }

    startTimer() {
        setInterval(() => {
            this.render();
        }, 3600000); // Update every hour
    }
} 