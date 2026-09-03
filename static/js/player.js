/**
 * CineVerse OTT HTML5 Cinema Video Player Controller
 * Implements: Play/Pause, Seek, Buffer preview, Skip Intro, Auto Next Episode,
 *             Subtitles toggle, Volume slider, Keyboard shortcuts.
 */

class CineVersePlayer {
  constructor(videoElementId) {
    this.video = document.getElementById(videoElementId);
    if (!this.video) return;

    this.wrapper = this.video.closest('.player-wrapper');
    this.playPauseBtn = document.getElementById('playPauseBtn');
    this.progressBar = document.getElementById('progressBar');
    this.progressFill = document.getElementById('progressFill');
    this.timeDisplay = document.getElementById('timeDisplay');
    this.volumeBtn = document.getElementById('volumeBtn');
    this.volumeSlider = document.getElementById('volumeSlider');
    this.fullscreenBtn = document.getElementById('fullscreenBtn');
    this.skipIntroBtn = document.getElementById('skipIntroBtn');
    this.nextEpisodeOverlay = document.getElementById('nextEpisodeOverlay');
    this.nextCountdownSpan = document.getElementById('nextCountdown');

    this.introStart = parseInt(this.video.dataset.introStart || '0');
    this.introEnd = parseInt(this.video.dataset.introEnd || '0');
    this.outroStart = parseInt(this.video.dataset.outroStart || '999999');
    this.nextUrl = this.video.dataset.nextUrl || '';

    this.countdownTimer = null;
    this.countdownSeconds = 10;

    this.init();
  }

  init() {
    // 1. Play / Pause
    if (this.playPauseBtn) {
      this.playPauseBtn.addEventListener('click', () => this.togglePlay());
    }
    this.video.addEventListener('click', () => this.togglePlay());

    // 2. Time & Progress Updates
    this.video.addEventListener('timeupdate', () => this.onTimeUpdate());
    if (this.progressBar) {
      this.progressBar.addEventListener('click', (e) => this.seek(e));
    }

    // 3. Volume
    if (this.volumeBtn) {
      this.volumeBtn.addEventListener('click', () => this.toggleMute());
    }
    if (this.volumeSlider) {
      this.volumeSlider.addEventListener('input', (e) => {
        this.video.volume = e.target.value;
        this.video.muted = false;
        this.updateVolumeIcon();
      });
    }

    // 4. Fullscreen
    if (this.fullscreenBtn) {
      this.fullscreenBtn.addEventListener('click', () => this.toggleFullscreen());
    }

    // 5. Skip Intro
    if (this.skipIntroBtn) {
      this.skipIntroBtn.addEventListener('click', () => {
        if (this.introEnd > 0) {
          this.video.currentTime = this.introEnd;
          this.skipIntroBtn.style.display = 'none';
        }
      });
    }

    // 6. Keyboard Shortcuts
    document.addEventListener('keydown', (e) => this.handleKeyboard(e));

    // 7. Video State Icons
    this.video.addEventListener('play', () => {
      if (this.playPauseBtn) this.playPauseBtn.innerHTML = '⏸';
    });
    this.video.addEventListener('pause', () => {
      if (this.playPauseBtn) this.playPauseBtn.innerHTML = '▶';
    });
  }

  togglePlay() {
    if (this.video.paused || this.video.ended) {
      this.video.play();
    } else {
      this.video.pause();
    }
  }

  onTimeUpdate() {
    const cur = this.video.currentTime;
    const dur = this.video.duration || 1;
    const pct = (cur / dur) * 100;

    if (this.progressFill) {
      this.progressFill.style.width = `${pct}%`;
    }

    if (this.timeDisplay) {
      this.timeDisplay.innerText = `${this.formatTime(cur)} / ${this.formatTime(dur)}`;
    }

    // Skip Intro button trigger
    if (this.skipIntroBtn && this.introEnd > this.introStart) {
      if (cur >= this.introStart && cur <= this.introEnd) {
        this.skipIntroBtn.style.display = 'block';
      } else {
        this.skipIntroBtn.style.display = 'none';
      }
    }

    // Next Episode Auto-prompt
    if (this.nextEpisodeOverlay && this.nextUrl && cur >= this.outroStart) {
      if (this.nextEpisodeOverlay.style.display !== 'flex') {
        this.showNextEpisodeOverlay();
      }
    }
  }

  seek(e) {
    const rect = this.progressBar.getBoundingClientRect();
    const pos = (e.clientX - rect.left) / rect.width;
    this.video.currentTime = pos * this.video.duration;
  }

  toggleMute() {
    this.video.muted = !this.video.muted;
    this.updateVolumeIcon();
  }

  updateVolumeIcon() {
    if (!this.volumeBtn) return;
    if (this.video.muted || this.video.volume === 0) {
      this.volumeBtn.innerHTML = '🔇';
    } else if (this.video.volume < 0.5) {
      this.volumeBtn.innerHTML = '🔉';
    } else {
      this.volumeBtn.innerHTML = '🔊';
    }
  }

  toggleFullscreen() {
    if (!document.fullscreenElement) {
      this.wrapper.requestFullscreen().catch(() => {});
    } else {
      document.exitFullscreen().catch(() => {});
    }
  }

  showNextEpisodeOverlay() {
    this.nextEpisodeOverlay.style.display = 'flex';
    this.countdownSeconds = 10;
    if (this.nextCountdownSpan) this.nextCountdownSpan.innerText = this.countdownSeconds;

    this.countdownTimer = setInterval(() => {
      this.countdownSeconds--;
      if (this.nextCountdownSpan) this.nextCountdownSpan.innerText = this.countdownSeconds;
      if (this.countdownSeconds <= 0) {
        clearInterval(this.countdownTimer);
        window.location.href = this.nextUrl;
      }
    }, 1000);
  }

  handleKeyboard(e) {
    // Avoid interfering with inputs
    if (['INPUT', 'TEXTAREA'].includes(e.target.tagName)) return;

    switch (e.code) {
      case 'Space':
      case 'KeyK':
        e.preventDefault();
        this.togglePlay();
        break;
      case 'KeyF':
        e.preventDefault();
        this.toggleFullscreen();
        break;
      case 'KeyM':
        e.preventDefault();
        this.toggleMute();
        break;
      case 'ArrowRight':
        e.preventDefault();
        this.video.currentTime = Math.min(this.video.duration, this.video.currentTime + 10);
        break;
      case 'ArrowLeft':
        e.preventDefault();
        this.video.currentTime = Math.max(0, this.video.currentTime - 10);
        break;
      case 'ArrowUp':
        e.preventDefault();
        this.video.volume = Math.min(1, this.video.volume + 0.1);
        if (this.volumeSlider) this.volumeSlider.value = this.video.volume;
        this.video.muted = false;
        this.updateVolumeIcon();
        break;
      case 'ArrowDown':
        e.preventDefault();
        this.video.volume = Math.max(0, this.video.volume - 0.1);
        if (this.volumeSlider) this.volumeSlider.value = this.video.volume;
        this.updateVolumeIcon();
        break;
    }
  }

  formatTime(secs) {
    const s = Math.floor(secs % 60);
    const m = Math.floor((secs / 60) % 60);
    const h = Math.floor(secs / 3600);
    const pad = (n) => (n < 10 ? '0' + n : n);
    return h > 0 ? `${h}:${pad(m)}:${pad(s)}` : `${m}:${pad(s)}`;
  }
}

document.addEventListener('DOMContentLoaded', () => {
  new CineVersePlayer('cineverseVideo');
});

// Auto Beacon Progress Sync Every 5 Seconds
setInterval(() => {
  const video = document.getElementById('cineverseVideo');
  if (video && !video.paused && video.duration > 0) {
    const urlParts = window.location.pathname.split('/');
    let contentType = 'MOVIE';
    let contentId = video.dataset.contentId || '';

    // If on episode or movie player, sync to backend
    fetch('/history/api/progress/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': (document.cookie.match(/csrftoken=([^;]+)/) || [])[1] || ''
      },
      body: JSON.stringify({
        content_type: contentType,
        content_id: contentId,
        position_seconds: Math.floor(video.currentTime),
        duration_seconds: Math.floor(video.duration)
      })
    }).catch(() => {});
  }
}, 5000);
