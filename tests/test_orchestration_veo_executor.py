import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.orchestration.veo_executor import (
    MissingVeoCredentialError,
    VeoExecutionError,
    VeoExecutor,
    extract_last_frame,
    save_video_from_operation,
)


def test_generate_without_credential_raises_clearly():
    executor = VeoExecutor(api_key=None)
    try:
        executor.generate("veo-3.1-fast-generate-preview", {"model": "x", "instances": []})
        assert False, "should have raised"
    except MissingVeoCredentialError as e:
        assert "GEMINI_API_KEY" in str(e) or "VEO_API_KEY" in str(e)


def test_extract_last_frame_real_ffmpeg(tmp_path):
    video_path = tmp_path / "test.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "lavfi", "-i", "testsrc=duration=1:size=160x120:rate=5", str(video_path)],
        capture_output=True, check=True,
    )
    frame_path = extract_last_frame(str(video_path), str(tmp_path / "frame.jpg"))
    assert frame_path.exists()
    assert frame_path.stat().st_size > 0


def test_extract_last_frame_missing_video_raises(tmp_path):
    try:
        extract_last_frame(str(tmp_path / "does_not_exist.mp4"), str(tmp_path / "frame.jpg"))
        assert False, "should have raised"
    except VeoExecutionError:
        pass


def test_save_video_from_operation_base64(tmp_path):
    import base64
    fake_bytes = b"fake video content for test"
    operation = {
        "response": {"generateVideoResponse": {"generatedSamples": [
            {"video": {"bytesBase64Encoded": base64.b64encode(fake_bytes).decode()}}
        ]}}
    }
    out_path = save_video_from_operation(operation, str(tmp_path / "out.mp4"))
    assert out_path.read_bytes() == fake_bytes


def test_save_video_from_operation_unexpected_shape_raises_clearly(tmp_path):
    try:
        save_video_from_operation({"response": {"somethingElse": True}}, str(tmp_path / "out.mp4"))
        assert False, "should have raised"
    except VeoExecutionError as e:
        assert "documented shape" in str(e)
