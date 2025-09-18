import cv2
import numpy as np
import mvsdk
import platform
from Filtros import filtros


def main_loop():
	# Enumerar cámaras
	DevList = mvsdk.CameraEnumerateDevice()
	print(DevList)
	nDev = len(DevList)
	if nDev < 1:
		print("No camera was found!")
		return

	for i, DevInfo in enumerate(DevList):
		print("{}: {} {}".format(i, DevInfo.GetFriendlyName(), DevInfo.GetPortType()))
	i = 0 if nDev == 1 else int(input("Select camera: "))
	DevInfo = DevList[i]
	print(DevInfo)

	#camara abierta
	hCamera = 0
	try:
		hCamera = mvsdk.CameraInit(DevInfo, -1, -1)
	except mvsdk.CameraException as e:
		print("CameraInit Failed({}): {}".format(e.error_code, e.message) )
		return

	# Obtener descripción de la función de la cámara
	cap = mvsdk.CameraGetCapability(hCamera)

	# Determinar si es una cámara en blanco y negro o una cámara a color
	monoCamera = (cap.sIspCapacity.bMonoSensor != 0)

	# La cámara monocromática permite al ISP emitir directamente datos MONO 
	# en lugar de expandirlos a una escala de grises de 24 bits de RGB.
	if monoCamera:
		mvsdk.CameraSetIspOutFormat(hCamera, mvsdk.CAMERA_MEDIA_TYPE_MONO8)
	else:
		mvsdk.CameraSetIspOutFormat(hCamera, mvsdk.CAMERA_MEDIA_TYPE_BGR8)

	# Cambie el modo de la cámara a adquisición continua
	mvsdk.CameraSetTriggerMode(hCamera, 0)

	# 手Exposición dinámica, tiempo de exposición 30 ms


	mvsdk.CameraSetAeState(hCamera, 0)
	#mvsdk.CameraSetExposureTime(hCamera, 30 * 1000)

	# Deje que el hilo de obtención de imágenes internas del SDK comience a funcionar
	mvsdk.CameraPlay(hCamera)

	# Calcular el tamaño requerido del búfer RGB, que se asigna directamente según la resolución máxima de la cámara
	FrameBufferSize = cap.sResolutionRange.iWidthMax * cap.sResolutionRange.iHeightMax * (1 if monoCamera else 3)

	# Asignar búfer RGB para almacenar la imagen de salida del ISP
	# Nota: Los datos transmitidos desde la cámara a la PC son datos RAW, que se convierten a datos RGB mediante el software del ISP en la PC (si es una cámara en blanco y negro, no es necesario convertir el formato, pero el ISP tiene otro procesamiento, por lo que este búfer también debe asignarse)


	pFrameBuffer = mvsdk.CameraAlignMalloc(FrameBufferSize, 16)

	while (cv2.waitKey(1) & 0xFF) != ord('q'):
		# Toma una fotografía con la cámara
		try:
			pRawData, FrameHead = mvsdk.CameraGetImageBuffer(hCamera, 200)
			mvsdk.CameraImageProcess(hCamera, pRawData, pFrameBuffer, FrameHead)
			mvsdk.CameraReleaseImageBuffer(hCamera, pRawData)

			# Los datos de imagen obtenidos en Windows están invertidos y almacenados en formato BMP.
			# Para convertirlos a OpenCV, es necesario invertirlos para corregirlos.
			# Salida positiva directa en Linux, sin necesidad de subir y bajar
			if platform.system() == "Windows":
				mvsdk.CameraFlipFrameBuffer(pFrameBuffer, FrameHead, 1)
			
			# En este punto, la imagen se ha almacenado en pFrameBuffer. 
			# Para una cámara a color, pFrameBuffer = datos RGB; para una cámara en blanco y negro, 
			# pFrameBuffer = datos en escala de grises de 8 bits.
			# Convierte pFrameBuffer al formato de imagen opencv para el posterior procesamiento del algoritmo


			frame_data = (mvsdk.c_ubyte * FrameHead.uBytes).from_address(pFrameBuffer)
			frame = np.frombuffer(frame_data, dtype=np.uint8)
			frame = frame.reshape((FrameHead.iHeight, FrameHead.iWidth, 1 if FrameHead.uiMediaType == mvsdk.CAMERA_MEDIA_TYPE_MONO8 else 3) )

			frame = cv2.resize(frame, (540,540), interpolation = cv2.INTER_LINEAR)
			if frame is not None:
				final = filtros(frame)
				cv2.imshow('Detection', final)

			
		except mvsdk.CameraException as e:
			if e.error_code != mvsdk.CAMERA_STATUS_TIME_OUT:
				print("CameraGetImageBuffer failed({}): {}".format(e.error_code, e.message) )

	# Apagar la cámara
	mvsdk.CameraUnInit(hCamera)

	# Liberar framebuffer
	mvsdk.CameraAlignFree(pFrameBuffer)

def main():
	try:
		main_loop()
	finally:
		cv2.destroyAllWindows()

main()

