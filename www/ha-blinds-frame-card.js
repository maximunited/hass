/* ha-blinds-frame-card.js – v20 ResizeObserver + forcePng + transparent host */
class HaBlindsFrameCard extends HTMLElement {
  setConfig(cfg) {
    this._cfg = Object.assign({
      fps: 25,
      frames: 100,
      cooldownMs: 2000,
      easing: true,
      speed: 0.5
    }, cfg);
  }

  set hass(hass) {
    if (!this._cfg || !this._cfg.entity) return;
    if (!this._built) this._build();

    const ent = hass.states[this._cfg.entity];
    if (!ent || ent.attributes.current_position === undefined) return;

    const pct = Number(ent.attributes.current_position);
    if (Number.isNaN(pct)) return;

    // HA cover: 100 = open → frame 0; 0 = closed → last frame
    const tgt = Math.round((100 - pct) * (this._cfg.frames - 1) / 100);

    if (!this._synced) {
      this._synced = true;
      this._current = tgt;
      this._seekInstant(tgt);
      return;
    }

    if (Date.now() < this._quietUntil || this._animating) return;
    if (tgt !== this._current) this._startGlide(tgt);
  }

  connectedCallback() {
    if (this._ro) return;
    this._ro = new ResizeObserver(() => {
      if (this._usePNG && this._synced) this._drawPNGFrame(this._current || 0);
    });
    this._ro.observe(this);
  }

  disconnectedCallback() {
    if (this._ro) {
      this._ro.disconnect();
      this._ro = null;
    }
  }

  _isMobile() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
           (navigator.userAgent.includes('Chrome') && /Mobile/i.test(navigator.userAgent));
  }

  _build() {
    this._built = true;
    this._frames = this._cfg.frames;
    this._stepSec = 1 / this._cfg.fps;
    this._usePNG = !!(this._cfg && this._cfg.forcePng) || this._isMobile();

    this.style.display = 'block';
    this.style.position = 'absolute';
    this.style.overflow = 'hidden';
    this.style.pointerEvents = 'none';
    this.style.background = 'transparent';
    if (!this.style.width) this.style.width = '100%';
    if (!this.style.height) this.style.height = '100%';
    this.style.margin = '0';
    this.style.padding = '0';
    this.style.boxSizing = 'border-box';

    if (this._usePNG) this._buildPNGVersion();
    else this._buildVideoVersion();

    this._current = 0;
    this._quietUntil = 0;
    this._animating = false;
    this._synced = false;
  }

  _innerWrap() {
    const wrap = document.createElement('div');
    Object.assign(wrap.style, {
      position: 'absolute',
      inset: '0',
      width: '100%',
      height: '100%',
      overflow: 'hidden',
      margin: '0',
      padding: '0',
      background: 'transparent'
    });
    return wrap;
  }

  _fillMediaStyle(el) {
    Object.assign(el.style, {
      position: 'absolute',
      inset: '0',
      width: '100%',
      height: '100%',
      objectFit: 'fill',
      pointerEvents: 'none',
      display: 'block',
      margin: '0',
      padding: '0',
      border: '0',
      background: 'transparent'
    });
  }

  _buildPNGVersion() {
    this._canvas = document.createElement('canvas');
    this._fillMediaStyle(this._canvas);

    this._pngFrames = [];
    this._loadedFrames = 0;
    this._pngPath = this._cfg.png_path || '/local/images/master-bedroom/north_blinds_';

    for (let i = 0; i < this._frames; i++) {
      const img = new Image();
      const frameNum = String(i).padStart(3, '0');
      img.src = `${this._pngPath}${frameNum}.png`;
      img.onload = () => {
        this._loadedFrames++;
        if (this._loadedFrames === this._frames) {
          this._allPNGsLoaded = true;
          this._drawPNGFrame(this._current || 0);
        }
      };
      img.onerror = () => {
        console.error(`Failed to load PNG frame: ${img.src}`);
      };
      this._pngFrames[i] = img;
    }

    const wrap = this._innerWrap();
    wrap.appendChild(this._canvas);
    this.appendChild(wrap);
  }

  _buildVideoVersion() {
    this._v = Object.assign(document.createElement('video'), {
      src: this._cfg.src,
      muted: true,
      loop: false,
      playsInline: true,
      preload: 'auto'
    });
    this._fillMediaStyle(this._v);

    this._v.addEventListener('loadeddata', () => {
      this._v.pause();
      this._seekInstant(this._current || 0);
    });

    this._canvas = document.createElement('canvas');
    this._fillMediaStyle(this._canvas);
    this._canvas.style.opacity = '0';

    const wrap = this._innerWrap();
    wrap.append(this._v, this._canvas);
    this.appendChild(wrap);
  }

  _seekInstant(frameIndex) {
    const f = Math.max(0, Math.min(this._frames - 1, frameIndex));
    this._current = f;
    if (this._usePNG) {
      this._drawPNGFrame(f);
      return;
    }
    if (!this._v) return;
    const apply = () => {
      this._v.pause();
      this._v.currentTime = f * this._stepSec;
      const onSeeked = () => {
        this._v.removeEventListener('seeked', onSeeked);
        this._freezeCurrentFrame();
      };
      this._v.addEventListener('seeked', onSeeked);
    };
    if (this._v.readyState >= 1) apply();
    else this._v.addEventListener('loadedmetadata', apply, { once: true });
  }

  _drawPNGFrame(frameIndex) {
    if (!this._allPNGsLoaded || frameIndex < 0 || frameIndex >= this._frames) return;
    const canvas = this._canvas;
    if (!canvas) return;
    const ctx = canvas.getContext('2d', { alpha: true });
    const img = this._pngFrames[frameIndex];
    if (!img || !img.complete || !img.naturalWidth) return;
    const rect = canvas.getBoundingClientRect();
    const w = Math.max(1, Math.round(rect.width) || this.clientWidth || img.naturalWidth);
    const h = Math.max(1, Math.round(rect.height) || this.clientHeight || img.naturalHeight);
    if (canvas.width !== w || canvas.height !== h) {
      canvas.width = w;
      canvas.height = h;
    }
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
  }

  _startGlide(target) {
    const start = this._current;
    const distance = target - start;
    const dir = Math.sign(distance);
    if (!dir) return;

    const pct = Math.abs(distance) / (this._cfg.frames - 1) * 100;
    const baseDuration = pct * 50;
    const totalMs = Math.max(200, baseDuration / this._cfg.speed);

    this._animating = true;
    this._quietUntil = Date.now() + this._cfg.cooldownMs;

    if (!this._usePNG && this._canvas) this._canvas.style.opacity = '0';

    const ease = t => this._cfg.easing
      ? (t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t) : t;

    const t0 = performance.now();
    const step = now => {
      const p = Math.min((now - t0) / totalMs, 1);
      const f = start + distance * ease(p);
      this._current = Math.round(f);

      if (this._usePNG) this._drawPNGFrame(this._current);
      else if (this._v) this._v.currentTime = f * this._stepSec;

      if (p < 1) requestAnimationFrame(step);
      else {
        this._animating = false;
        this._current = target;
        if (!this._usePNG) this._freezeCurrentFrame();
      }
    };

    if (!this._usePNG && this._v) {
      this._v.pause();
      this._v.currentTime = start * this._stepSec;
    }
    requestAnimationFrame(step);
  }

  _freezeCurrentFrame() {
    if (this._usePNG || !this._v || !this._canvas) return;
    const video = this._v;
    const cvs = this._canvas;
    if (!video.videoWidth) return;
    cvs.width = video.videoWidth;
    cvs.height = video.videoHeight;
    const ctx = cvs.getContext('2d');
    ctx.drawImage(video, 0, 0, cvs.width, cvs.height);
    video.pause();
    cvs.style.opacity = '1';
  }

  getCardSize() { return 2; }
}

if (!customElements.get('ha-blinds-frame-card')) {
  customElements.define('ha-blinds-frame-card', HaBlindsFrameCard);
}
