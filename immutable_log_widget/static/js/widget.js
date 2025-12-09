/**
 * Immutable Log Viewer - Client-side JavaScript
 * 
 * Handles log streaming, infinite scroll, integrity verification,
 * and user interactions.
 */

class LogViewer {
    constructor(config) {
        this.config = config;
        this.apiBaseUrl = config.apiBaseUrl;
        this.totalLines = config.totalLines;
        this.enableDownload = config.enableDownload;
        
        this.loadedLines = 0;
        this.isLoading = false;
        this.hasMore = true;
        this.chunkSize = 1000;
        
        this.logContent = document.getElementById('log-content');
        this.loadingIndicator = document.getElementById('loading-indicator');
        this.emptyState = document.getElementById('empty-state');
        this.progressBar = document.getElementById('progress-bar');
        this.statusMessage = document.getElementById('status-message');
        this.loadedLinesSpan = document.getElementById('loaded-lines');
        
        this.verifyBtn = document.getElementById('verify-btn');
        this.downloadBtn = document.getElementById('download-btn');
        this.refreshBtn = document.getElementById('refresh-btn');
        
        this.init();
    }
    
    init() {
        this.verifyBtn.addEventListener('click', () => this.verifyIntegrity());
        
        if (this.downloadBtn) {
            this.downloadBtn.addEventListener('click', () => this.downloadLog());
        }
        
        this.refreshBtn.addEventListener('click', () => this.refresh());
        
        this.logContent.parentElement.addEventListener('scroll', (e) => {
            this.handleScroll(e);
        });
        
        this.loadLogs();
    }
    
    async loadLogs() {
        if (this.isLoading || !this.hasMore) return;
        
        this.isLoading = true;
        this.showLoading();
        
        try {
            const url = `${this.apiBaseUrl}/api/stream?start=${this.loadedLines}&count=${this.chunkSize}&validate=true`;
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.lines && data.lines.length > 0) {
                data.lines.forEach(line => this.renderLine(line));
                this.loadedLines += data.lines.length;
                this.hasMore = data.has_more;
                this.updateStats();
            } else {
                this.hasMore = false;
                if (this.loadedLines === 0) {
                    this.showEmptyState();
                }
            }
            
        } catch (error) {
            this.showError(`Failed to load logs: ${error.message}`);
            console.error('Error loading logs:', error);
        } finally {
            this.isLoading = false;
            this.hideLoading();
        }
    }
    
    renderLine(lineData) {
        const lineDiv = document.createElement('div');
        lineDiv.className = 'log-line';
        
        if (lineData.log_level) {
            lineDiv.classList.add(`log-${lineData.log_level.toLowerCase()}`);
        }
        
        if (lineData.is_valid === false) {
            lineDiv.classList.add('tampered');
        }
        
        const lineNumber = document.createElement('span');
        lineNumber.className = 'log-line-number';
        lineNumber.textContent = lineData.line_number;
        
        const lineContent = document.createElement('span');
        lineContent.className = 'log-line-content';
        lineContent.textContent = lineData.content;
        
        lineDiv.appendChild(lineNumber);
        lineDiv.appendChild(lineContent);
        
        this.logContent.appendChild(lineDiv);
    }
    
    async verifyIntegrity() {
        this.verifyBtn.disabled = true;
        this.showProgress('Verifying integrity...');
        
        try {
            const url = `${this.apiBaseUrl}/api/verify`;
            const response = await fetch(url, { method: 'POST' });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            
            if (result.valid) {
                this.showSuccess(
                    `✓ Log integrity verified! All ${result.total_lines} lines are valid. ` +
                    `(Checked in ${result.check_duration_ms}ms)`
                );
            } else {
                this.showWarning(
                    `⚠️ Integrity check failed! Found ${result.tampered_lines.length} tampered lines: ` +
                    `${result.tampered_lines.slice(0, 10).join(', ')}` +
                    `${result.tampered_lines.length > 10 ? '...' : ''}`
                );
                
                this.highlightTamperedLines(result.tampered_lines);
            }
            
        } catch (error) {
            this.showError(`Verification failed: ${error.message}`);
            console.error('Error verifying integrity:', error);
        } finally {
            this.verifyBtn.disabled = false;
            this.hideProgress();
        }
    }
    
    highlightTamperedLines(tamperedLineNumbers) {
        const allLines = this.logContent.querySelectorAll('.log-line');
        
        tamperedLineNumbers.forEach(lineNum => {
            const lineElement = Array.from(allLines).find(el => {
                const lineNumSpan = el.querySelector('.log-line-number');
                return lineNumSpan && parseInt(lineNumSpan.textContent) === lineNum;
            });
            
            if (lineElement) {
                lineElement.classList.add('tampered');
            }
        });
    }
    
    downloadLog() {
        if (!this.enableDownload) {
            this.showError('Download is disabled');
            return;
        }
        
        const url = `${this.apiBaseUrl}/api/download`;
        window.location.href = url;
        this.showSuccess('Download started...');
    }
    
    refresh() {
        this.logContent.innerHTML = '';
        this.loadedLines = 0;
        this.hasMore = true;
        this.hideStatusMessage();
        
        this.loadLogs();
    }
    
    handleScroll(e) {
        const container = e.target;
        const scrollPosition = container.scrollTop + container.clientHeight;
        const scrollHeight = container.scrollHeight;
        
        if (scrollPosition >= scrollHeight * 0.8 && this.hasMore && !this.isLoading) {
            this.loadLogs();
        }
    }
    
    updateStats() {
        this.loadedLinesSpan.textContent = this.loadedLines;
    }
    
    showLoading() {
        this.loadingIndicator.classList.remove('hidden');
    }
    
    hideLoading() {
        this.loadingIndicator.classList.add('hidden');
    }
    
    showEmptyState() {
        this.emptyState.classList.remove('hidden');
    }
    
    showProgress(message) {
        this.progressBar.classList.remove('hidden');
        const progressText = this.progressBar.querySelector('.progress-text');
        if (progressText) {
            progressText.textContent = message;
        }
    }
    
    hideProgress() {
        this.progressBar.classList.add('hidden');
    }
    
    showStatusMessage(message, type) {
        this.statusMessage.textContent = message;
        this.statusMessage.className = `status-message ${type}`;
        this.statusMessage.classList.remove('hidden');
        
        setTimeout(() => this.hideStatusMessage(), 5000);
    }
    
    hideStatusMessage() {
        this.statusMessage.classList.add('hidden');
    }
    
    showSuccess(message) {
        this.showStatusMessage(message, 'success');
    }
    
    showError(message) {
        this.showStatusMessage(message, 'error');
    }
    
    showWarning(message) {
        this.showStatusMessage(message, 'warning');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    if (window.LOG_VIEWER_CONFIG) {
        new LogViewer(window.LOG_VIEWER_CONFIG);
    } else {
        console.error('LOG_VIEWER_CONFIG not found');
    }
});
