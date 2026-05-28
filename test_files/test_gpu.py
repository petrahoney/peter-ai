import torch
import whisper

print('PyTorch:', torch.__version__)
print('CUDA:', torch.cuda.is_available())

if torch.cuda.is_available():
    print('GPU:', torch.cuda.get_device_name(0))
else:
    print('GPU: Tidak terdeteksi')

print('Loading Whisper model medium...')
model = whisper.load_model('medium')
print('Model device:', next(model.parameters()).device)
print('Whisper + GPU siap!')