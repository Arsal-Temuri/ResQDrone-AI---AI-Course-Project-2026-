from pathlib import Path

from PyQt6.QtCore import QObject, QEvent, Qt, QUrl
from PyQt6.QtWidgets import QAbstractButton

try:
    from PyQt6.QtMultimedia import QSoundEffect
except ImportError:  # pragma: no cover - optional Qt multimedia support
    QSoundEffect = None


class AudioManager(QObject):
    """Centralized UI audio helper for startup and button click sounds."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._theme_played = False
        self._enabled = QSoundEffect is not None
        self._theme_effect = None
        self._click_effect = None

        if not self._enabled:
            return

        assets_dir = Path(__file__).resolve().parent.parent / "assets"
        theme_path = assets_dir / "theme.wav"
        click_path = assets_dir / "click.wav"

        self._theme_effect = QSoundEffect(self)
        self._theme_effect.setVolume(0.65)
        if theme_path.exists():
            self._theme_effect.setSource(QUrl.fromLocalFile(str(theme_path)))

        self._click_effect = QSoundEffect(self)
        self._click_effect.setVolume(0.55)
        if click_path.exists():
            self._click_effect.setSource(QUrl.fromLocalFile(str(click_path)))

    def eventFilter(self, obj, event):
        if not self._enabled or self._click_effect is None:
            return super().eventFilter(obj, event)

        if event.type() == QEvent.Type.MouseButtonRelease:
            if isinstance(obj, QAbstractButton) and obj.isEnabled():
                if event.button() == Qt.MouseButton.LeftButton:
                    self.play_click()

        return super().eventFilter(obj, event)

    def play_theme(self):
        if not self._enabled or self._theme_effect is None or self._theme_played:
            return

        self._theme_played = True
        self._theme_effect.play()

    def play_click(self):
        if not self._enabled or self._click_effect is None:
            return

        self._click_effect.play()
