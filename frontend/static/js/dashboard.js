// Dashboard JavaScript
class Dashboard {
    constructor() {
        this.modal = document.getElementById('match-modal');
        this.modalBody = document.getElementById('modal-body');
        this.modalTitle = document.getElementById('modal-match-title');
        this.init();
    }

    async init() {
        await this.loadMetrics();
        await this.loadMatches();
        this.setupModal();
    }

    async loadMetrics() {
        try {
            const response = await fetch('/api/metrics');
            const metrics = await response.json();
            this.renderMetrics(metrics);
        } catch (error) {
            console.error('Error loading metrics:', error);
            this.showError('metrics-grid', 'Failed to load metrics');
        }
    }

    async loadMatches() {
        try {
            const response = await fetch('/api/matches');
            const matches = await response.json();
            this.renderMatches(matches);
        } catch (error) {
            console.error('Error loading matches:', error);
            this.showError('matches-list', 'Failed to load matches');
        }
    }

    renderMetrics(metrics) {
        const metricsGrid = document.getElementById('metrics-grid');
        
        const formatCurrency = (amount) => `$${amount.toLocaleString()}`;
        const formatPercentage = (rate) => `${rate}%`;
        
        const profitLoss = metrics.current_balance - metrics.starting_balance;
        const profitLossClass = profitLoss >= 0 ? 'positive' : 'negative';
        
        metricsGrid.innerHTML = `
            <div class="metric-card">
                <div class="metric-label">Win Rate</div>
                <div class="metric-value">${formatPercentage(metrics.win_rate)}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Current Balance</div>
                <div class="metric-value">${formatCurrency(metrics.current_balance)}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Starting Balance</div>
                <div class="metric-value">${formatCurrency(metrics.starting_balance)}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Profit/Loss</div>
                <div class="metric-value ${profitLossClass}">${formatCurrency(profitLoss)}</div>
            </div>
        `;
    }

    renderMatches(matches) {
        const matchesList = document.getElementById('matches-list');
        
        if (matches.length === 0) {
            matchesList.innerHTML = '<div class="loading">No matches available</div>';
            return;
        }

        const matchesHtml = matches.map(match => {
            // Show final score for completed games, odds for upcoming games
            const rightDisplay = match.status === 'completed' && (match.home_score || match.away_score) 
                ? `<div class="match-score">${match.home_score || 0} - ${match.away_score || 0}</div>`
                : `<div class="match-odds">${match.odds}</div>`;
            
            return `
                <div class="match-card" data-match-id="${match.id}" onclick="dashboard.openMatchDetail('${match.id}')">
                    <div class="match-header">
                        <div class="match-teams">${match.team1} vs ${match.team2}</div>
                        ${rightDisplay}
                    </div>
                    <div class="match-details">
                        <div class="match-datetime">${match.date} at ${match.time}</div>
                        <div class="match-status ${match.status}">${match.status}</div>
                    </div>
                </div>
            `;
        }).join('');

        matchesList.innerHTML = matchesHtml;
    }

    setupModal() {
        // Close modal when clicking the X
        const closeBtn = document.querySelector('.close');
        closeBtn.onclick = () => this.closeModal();

        // Close modal when clicking outside
        window.onclick = (event) => {
            if (event.target === this.modal) {
                this.closeModal();
            }
        };

        // Close modal with Escape key
        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape' && this.modal.style.display === 'block') {
                this.closeModal();
            }
        });
    }

    async openMatchDetail(matchId) {
        this.modal.style.display = 'block';
        this.modalBody.innerHTML = '<div class="loading">Loading match details...</div>';
        
        try {
            const response = await fetch(`/api/match/${matchId}`);
            if (!response.ok) {
                throw new Error('Failed to fetch match details');
            }
            const matchDetail = await response.json();
            this.renderMatchDetail(matchDetail);
        } catch (error) {
            console.error('Error loading match detail:', error);
            this.modalBody.innerHTML = '<div class="loading">Error: Failed to load match details</div>';
        }
    }

    renderMatchDetail(match) {
        this.modalTitle.textContent = `${match.teams.home.name} vs ${match.teams.away.name}`;
        
        const formatOdds = (odds) => odds ? (odds > 2 ? `+${Math.round((odds - 1) * 100)}` : `${Math.round((odds - 1) * 100)}`) : 'N/A';
        
        this.modalBody.innerHTML = `
            <div class="match-detail-header">
                <div class="team-info">
                    <div class="team-name">${match.teams.home.name}</div>
                    <div class="team-city">${match.teams.home.city}</div>
                    ${match.teams.home.score !== null ? `<div class="score-display">${match.teams.home.score}</div>` : ''}
                </div>
                <div class="match-score">
                    <div class="match-time">${match.match_info.date} at ${match.match_info.time}</div>
                    <div class="match-status ${match.match_info.status}">${match.match_info.status}</div>
                    ${match.match_info.venue ? `<div class="venue">${match.match_info.venue}</div>` : ''}
                </div>
                <div class="team-info">
                    <div class="team-name">${match.teams.away.name}</div>
                    <div class="team-city">${match.teams.away.city}</div>
                    ${match.teams.away.score !== null ? `<div class="score-display">${match.teams.away.score}</div>` : ''}
                </div>
            </div>

            <div class="detail-grid">
                ${this.renderBettingOdds(match.betting_odds)}
                ${this.renderPredictions(match.predictions)}
                ${this.renderMatchFeatures(match.match_features)}
            </div>

            <div class="detail-section">
                <h3>Team Rosters</h3>
                ${this.renderPlayers(match.players)}
            </div>
        `;
    }

    renderBettingOdds(odds) {
        if (!odds || Object.keys(odds).length === 0) {
            return `
                <div class="detail-section">
                    <h3>Betting Odds</h3>
                    <p>No betting odds available</p>
                </div>
            `;
        }

        const formatOdds = (odds) => odds ? (odds > 2 ? `+${Math.round((odds - 1) * 100)}` : `${Math.round((odds - 1) * 100)}`) : 'N/A';

        return `
            <div class="detail-section">
                <h3>Betting Odds</h3>
                <div class="betting-odds-grid">
                    ${odds.moneyline ? `
                        <div class="odds-card">
                            <div class="odds-label">Home ML</div>
                            <div class="odds-value">${formatOdds(odds.moneyline.home)}</div>
                        </div>
                        <div class="odds-card">
                            <div class="odds-label">Away ML</div>
                            <div class="odds-value">${formatOdds(odds.moneyline.away)}</div>
                        </div>
                    ` : ''}
                    ${odds.spread ? `
                        <div class="odds-card">
                            <div class="odds-label">Home Spread</div>
                            <div class="odds-value">${odds.spread.home_line || 'N/A'}</div>
                        </div>
                        <div class="odds-card">
                            <div class="odds-label">Away Spread</div>
                            <div class="odds-value">${odds.spread.away_line || 'N/A'}</div>
                        </div>
                    ` : ''}
                    ${odds.totals ? `
                        <div class="odds-card">
                            <div class="odds-label">Over/Under</div>
                            <div class="odds-value">${odds.totals.over_under || 'N/A'}</div>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    renderPredictions(predictions) {
        return `
            <div class="detail-section">
                <h3>AI Predictions</h3>
                <div class="stat-item">
                    <span class="stat-label">Predicted Winner</span>
                    <span class="stat-value">${predictions.model_prediction}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Confidence</span>
                    <span class="stat-value">${predictions.confidence}%</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Home Win Probability</span>
                    <span class="stat-value">${predictions.win_probability.home}%</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Away Win Probability</span>
                    <span class="stat-value">${predictions.win_probability.away}%</span>
                </div>
            </div>
        `;
    }

    renderMatchFeatures(features) {
        return `
            <div class="detail-section">
                <h3>Match Analytics</h3>
                <div class="stat-item">
                    <span class="stat-label">Head-to-Head Record</span>
                    <span class="stat-value">${features.head_to_head.home_wins}-${features.head_to_head.away_wins}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Home Form (Last 5)</span>
                    <span class="stat-value">${features.form_guide.home_last_5}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Away Form (Last 5)</span>
                    <span class="stat-value">${features.form_guide.away_last_5}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Home Avg Points</span>
                    <span class="stat-value">${features.key_stats.home_avg_points}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Away Avg Points</span>
                    <span class="stat-value">${features.key_stats.away_avg_points}</span>
                </div>
            </div>
        `;
    }

    renderPlayers(players) {
        const homePlayersHtml = players.home.map(player => `
            <div class="player-item">
                <div>
                    <div class="player-name">${player.name}</div>
                    <div class="player-details">${player.position} ${player.jersey_number ? `#${player.jersey_number}` : ''}</div>
                </div>
                <div class="player-details">
                    ${player.height ? `${player.height}"` : ''} ${player.weight ? `${player.weight}lbs` : ''}
                </div>
            </div>
        `).join('');

        const awayPlayersHtml = players.away.map(player => `
            <div class="player-item">
                <div>
                    <div class="player-name">${player.name}</div>
                    <div class="player-details">${player.position} ${player.jersey_number ? `#${player.jersey_number}` : ''}</div>
                </div>
                <div class="player-details">
                    ${player.height ? `${player.height}"` : ''} ${player.weight ? `${player.weight}lbs` : ''}
                </div>
            </div>
        `).join('');

        return `
            <div class="players-grid">
                <div class="team-players">
                    <h4>Home Team</h4>
                    <div class="player-list">
                        ${homePlayersHtml || '<div class="player-item">No player data available</div>'}
                    </div>
                </div>
                <div class="team-players">
                    <h4>Away Team</h4>
                    <div class="player-list">
                        ${awayPlayersHtml || '<div class="player-item">No player data available</div>'}
                    </div>
                </div>
            </div>
        `;
    }

    closeModal() {
        this.modal.style.display = 'none';
    }

    showError(containerId, message) {
        const container = document.getElementById(containerId);
        container.innerHTML = `<div class="loading">Error: ${message}</div>`;
    }
}

// Initialize dashboard when DOM is loaded
let dashboard;
document.addEventListener('DOMContentLoaded', () => {
    dashboard = new Dashboard();
});