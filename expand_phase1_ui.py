import os

css_extra = '''
/* ==========================================================================
   CineVerse Comprehensive OTT Components & Video Player HUD Extensions
   ========================================================================== */

/* Shimmer Loading Skeletons */
.skeleton {
  background: linear-gradient(90deg, rgba(255, 255, 255, 0.04) 25%, rgba(255, 255, 255, 0.09) 50%, rgba(255, 255, 255, 0.04) 75%);
  background-size: 200% 100%;
  animation: skeletonPulse 1.8s infinite;
  border-radius: var(--cv-radius-sm);
}

@keyframes skeletonPulse {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.skeleton-card {
  width: 100%;
  aspect-ratio: 2/3;
  border-radius: var(--cv-radius-md);
}

.skeleton-text {
  height: 1rem;
  margin-bottom: 0.5rem;
  border-radius: var(--cv-radius-sm);
}

.skeleton-title {
  height: 1.5rem;
  width: 65%;
  margin-bottom: 0.75rem;
}

/* Horizontal Content Rail / Slider */
.content-rail-section {
  margin-bottom: 3.5rem;
  position: relative;
}

.content-rail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 1.25rem;
  padding: 0 0.5rem;
}

.content-rail-title {
  font-size: 1.45rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.content-rail-title .accent-bar {
  width: 4px;
  height: 1.25rem;
  background-color: var(--cv-primary);
  border-radius: 2px;
}

.content-rail-see-all {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--cv-primary);
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.content-rail-see-all:hover {
  text-decoration: underline;
}

.content-rail-scroll {
  display: flex;
  gap: 1.25rem;
  overflow-x: auto;
  scroll-behavior: smooth;
  padding: 1rem 0.5rem 1.5rem 0.5rem;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.content-rail-scroll::-webkit-scrollbar {
  display: none;
}

.rail-item {
  flex: 0 0 calc(100% / 6 - 1.1rem);
  min-width: 170px;
  position: relative;
  border-radius: var(--cv-radius-md);
  overflow: hidden;
  background-color: var(--cv-bg-card);
  transition: transform 0.3s cubic-bezier(0.2, 0.8, 0.2, 1), box-shadow 0.3s ease;
  aspect-ratio: 2/3;
  cursor: pointer;
}

@media (max-width: 1200px) {
  .rail-item { flex: 0 0 calc(100% / 4 - 1rem); }
}
@media (max-width: 768px) {
  .rail-item { flex: 0 0 calc(100% / 2.5 - 0.75rem); }
}

.rail-item:hover {
  transform: scale(1.08) translateY(-6px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.9), 0 0 25px rgba(229, 9, 20, 0.25);
  z-index: 50;
}

.rail-item-poster {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Modal Window System */
.cv-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(10px);
  display: none;
  align-items: center;
  justify-content: center;
  z-index: 3000;
  padding: 1.5rem;
}

.cv-modal-backdrop.active {
  display: flex;
}

.cv-modal {
  background: var(--cv-bg-surface);
  border: 1px solid var(--cv-border);
  border-radius: var(--cv-radius-lg);
  max-width: 680px;
  width: 100%;
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.9);
  animation: modalEnter 0.25s cubic-bezier(0.2, 0.8, 0.2, 1);
}

@keyframes modalEnter {
  from { transform: scale(0.92); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

.cv-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  border-bottom: 1px solid var(--cv-border);
}

.cv-modal-body {
  padding: 2rem;
  max-height: 75vh;
  overflow-y: auto;
}

.cv-modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.25rem 2rem;
  border-top: 1px solid var(--cv-border);
  background: rgba(255, 255, 255, 0.02);
}

/* Video Player Extended Control Elements */
.player-wrapper {
  position: relative;
  width: 100%;
  max-width: 100%;
  background: #000;
  overflow: hidden;
  border-radius: var(--cv-radius-md);
  box-shadow: 0 25px 60px rgba(0, 0, 0, 0.95);
}

.player-video {
  width: 100%;
  height: auto;
  display: block;
}

.player-hud {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(0,0,0,0.7) 0%, transparent 20%, transparent 80%, rgba(0,0,0,0.85) 100%);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 1.5rem;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.player-wrapper:hover .player-hud,
.player-wrapper.active-controls .player-hud {
  opacity: 1;
}

.player-top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.player-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #fff;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);
}

.player-bottom-bar {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.player-progress-bar {
  position: relative;
  width: 100%;
  height: 6px;
  background: rgba(255, 255, 255, 0.25);
  border-radius: 3px;
  cursor: pointer;
  transition: height 0.15s ease;
}

.player-progress-bar:hover {
  height: 10px;
}

.player-progress-fill {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  background: var(--cv-primary);
  border-radius: 3px;
}

.player-progress-handle {
  position: absolute;
  top: 50%;
  width: 14px;
  height: 14px;
  background: #fff;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.8);
  display: none;
}

.player-progress-bar:hover .player-progress-handle {
  display: block;
}

.player-controls-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.player-controls-left, .player-controls-right {
  display: flex;
  align-items: center;
  gap: 1.25rem;
}

.player-control-btn {
  background: none;
  border: none;
  color: #fff;
  font-size: 1.25rem;
  cursor: pointer;
  transition: color 0.2s ease, transform 0.15s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.player-control-btn:hover {
  color: var(--cv-primary);
  transform: scale(1.1);
}

.player-time-display {
  font-size: 0.85rem;
  font-family: monospace;
  color: rgba(255, 255, 255, 0.85);
}

.skip-intro-btn {
  position: absolute;
  bottom: 5.5rem;
  right: 2rem;
  background: rgba(16, 18, 23, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: #fff;
  padding: 0.65rem 1.4rem;
  border-radius: var(--cv-radius-sm);
  font-size: 0.9rem;
  font-weight: 700;
  cursor: pointer;
  backdrop-filter: blur(8px);
  transition: var(--cv-transition);
  z-index: 60;
}

.skip-intro-btn:hover {
  background: var(--cv-primary);
  border-color: var(--cv-primary);
  box-shadow: 0 0 15px var(--cv-primary-glow);
}
'''

with open('static/css/main.css', 'a', encoding='utf-8') as f:
    f.write('\n' + css_extra.strip() + '\n')

print("main.css extended with OTT Rail & Player styling.")
