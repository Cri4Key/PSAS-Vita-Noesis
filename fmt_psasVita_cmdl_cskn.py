# PlayStation All-Stars Battle Royale (PS Vita) importer + exporter
# Original importer by chrrox, fixed/improved by Cri4Key
# Exporter by Cri4Key
# Model type: BlePoint Engine model (MODL v8)

from inc_noesis import *
import collections
import struct
import os

def registerNoesisTypes():
	handle = noesis.register("PSASBR Vita Model (w/ Skeleton)", ".cskn")
	noesis.setHandlerTypeCheck(handle, psaVitamodCheckType)
	noesis.setHandlerLoadModel(handle, psasVitaLoadSkn)
	#noesis.setHandlerWriteModel(handle, psasVitaWriteSkn)
	#noesis.setTypeSharedModelFlags(handle, noesis.NMSHAREDFL_REVERSEWINDING)
	#noesis.setTypeSharedModelFlags(handle, noesis.NMSHAREDFL_FLATWEIGHTS_FORCE4)

	handle = noesis.register("PSASBR Vita Model", ".cmdl")
	noesis.setHandlerTypeCheck(handle, psaVitamodCheckType)
	noesis.setHandlerLoadModel(handle, psasVitaLoadMdl)
	#noesis.setHandlerWriteModel(handle, psasVitaWriteMdl)
	#noesis.setTypeSharedModelFlags(handle, noesis.NMSHAREDFL_REVERSEWINDING)

	'''handle = noesis.register("PSASBR Vita Texture", ".ctxr")
	noesis.setHandlerTypeCheck(handle, psaVitatexCheckType)
	noesis.setHandlerLoadRGBA(handle, psaVitatexLoadRGBA)'''


	#noesis.logPopup()

	return 1

MODL_HEADER = 0x4D4F444C
MODL_VERSION = 0x00000008


def psaVitamodCheckType(data):
	if len(data) < 8:
		return 0
	td = NoeBitStream(data, NOE_BIGENDIAN)

	if td.readInt() != MODL_HEADER:
		return 0
	if td.readInt() != MODL_VERSION:
		return 0
	return 1

def psaVitatexCheckType(data):
	td = NoeBitStream(data)
	return 1


class psasVitaWriteClass:

	def __init__(self, mdl, bs, skel):
		self.mdl = mdl
		self.bs = bs
		self.skel = skel

	def psasVitamodWriteModel(self, mdl, bs, skel):
		print("\nCalculating sizes and offsets...")
		# Order: POS0, NRM0, TAN0, COL0, TEX0, BONI, BONW
		meshesSize = [0] * 7
		meshesCount = 0
		alignedSize = []
		meshesOffs = []
		meshTable = 0

		# Calculate the size for each mesh block
		for mesh in mdl.meshes:
			for vcmp in mesh.positions:
				meshesSize[0] += len(vcmp.toBytes())

			for vcmp in mesh.normals:
				meshesSize[1] += len(vcmp.toBytes())

			for vcmp in mesh.tangents:
				meshesSize[2] += len(vcmp.toBytes())

			for vcmp in mesh.colors:
				meshesSize[3] += len(vcmp.toBytes())

			for vcmp in mesh.uvs:
				meshesSize[4] += len(vcmp.toBytes())

			if skel:
				for vcmp in mesh.weights:
					if vcmp.numWeights() > 4:
						print("\nERROR: Can't export models using more than 4 weights per vert to CSKN")
						return 0
					meshesSize[5] += len(vcmp.indices)
					meshesSize[6] += len(vcmp.weights)

		numVert = meshesSize[0] // 12
		if meshesSize[1] != 0:
			meshesSize[1] = numVert * 8
		if meshesSize[2] != 0:
			meshesSize[2] = numVert * 8
		meshesSize[3] //= 4
		if meshesSize[4] != 0:
			meshesSize[4] = numVert * 4
		if meshesSize[5] != 0:
			meshesSize[5] = numVert * 8
		if meshesSize[6] != 0:
			meshesSize[6] = numVert * 16
		print(meshesSize)

		# Calculate the size with padding for each mesh block and mesh table size
		# Look for the last block index, which doesn't use padding
		tempData = 0
		for i in range(0, len(meshesSize)):
			if meshesSize[i] != 0:
				meshesCount += 1
				meshTable += 16
				lastBlock = i

		for i in range(0, lastBlock + 1):
			if meshesSize[i] != 0:
				if i != lastBlock:
					alignedSize.append(self.calcPadSize(meshesSize[i]))
					meshTable += alignedSize[i]
				else:
					alignedSize.append(meshesSize[i])
					meshTable += alignedSize[i]
			else:
				alignedSize.append(-1)
		meshTable += 16
		print(alignedSize)

		# Calculate the offsets for each block
		tempData = 0
		for i in range(0, len(meshesSize)):
			if meshesSize[i] != 0:
				meshesOffs.append(16 + (meshesCount * 16) + tempData)
				tempData += alignedSize[i]
			else:
				meshesOffs.append(-1)

		# Write the header
		bs.setEndian(NOE_BIGENDIAN)
		bs.writeInt(MODL_HEADER)
		bs.writeInt(MODL_VERSION)
		bs.writeInt(0)
		bs.writeInt(meshTable)

		# Write the meshes information
		bs.setEndian(NOE_LITTLEENDIAN)
		bs.writeInt(meshesCount)

		# Write Position info
		bs.writeString("0SOP", 0)
		bs.writeShort(1)
		bs.writeShort(2)
		bs.writeInt(meshesOffs[0])
		bs.writeInt(meshesSize[0])
		# Write Normal info
		if meshesSize[1] != 0:
			bs.writeString("0MRN", 0)
			bs.writeShort(6)
			bs.writeShort(2)
			bs.writeInt(meshesOffs[1])
			bs.writeInt(meshesSize[1])
		# Write Tangent info
		if meshesSize[2] != 0:
			bs.writeString("0NAT", 0)
			bs.writeShort(6)
			bs.writeShort(2)
			bs.writeInt(meshesOffs[2])
			bs.writeInt(meshesSize[2])
		# Write Color info
		if meshesSize[3] != 0:
			bs.writeString("0LOC", 0)
			bs.writeShort(3)
			bs.writeShort(2)
			bs.writeInt(meshesOffs[3])
			bs.writeInt(meshesSize[3])
		# Write UV info
		if meshesSize[4] != 0:
			bs.writeString("0XET", 0)
			bs.writeShort(5)
			bs.writeShort(2)
			bs.writeInt(meshesOffs[4])
			bs.writeInt(meshesSize[4])
		# Write Blend Indices info
		if meshesSize[5] != 0:
			bs.writeString("INOB", 0)
			bs.writeShort(10)
			bs.writeShort(2)
			bs.writeInt(meshesOffs[5])
			bs.writeInt(meshesSize[5])
		# Write Blend Weights info
		if meshesSize[6] != 0:
			bs.writeString("WNOB", 0)
			bs.writeShort(2)
			bs.writeShort(2)
			bs.writeInt(meshesOffs[6])
			bs.writeInt(meshesSize[6])
		# Write padding
		bs.writeInt64(-1)
		bs.writeInt(-1)

		# Write mesh blocks
		print("Writing positions...")
		for mesh in mdl.meshes:
			for vcmp in mesh.positions:
				bs.writeBytes(vcmp.toBytes())
		for i in range(0, alignedSize[0] - meshesSize[0]):
			bs.writeByte(-1)

		if meshesSize[1] != 0:
			print("Writing normals...")
			vcmpdata = bytearray()
			for mesh in mdl.meshes:
				for vcmp in mesh.normals:
					vcmpdata += vcmp.toBytes()
			nrmData = NoeBitStream(vcmpdata)
			for i in range(0, meshesSize[1] // 2):
				# Every 3 UShort written, write 1 padding UShort
				if not ((((i+1) % 4) == 0) and i != 0):
					nrmBytes = noesis.encodeFloat16(nrmData.readFloat())
					bs.writeUShort(nrmBytes)
				else:
					bs.writeUShort(0)
			for i in range(0, alignedSize[1] - meshesSize[1]):
				bs.writeByte(-1)

		if meshesSize[2] != 0:
			print("Writing tangents...")
			vcmpdata = bytearray()
			for mesh in mdl.meshes:
				for vcmp in mesh.tangents:
					tangentdata = vcmp[2].toVec4()
					if vcmp[0].cross(vcmp[2]).dot(vcmp[1]) >= 0.0:
						tangentdata[3] = 1.0
					else:
						tangentdata[3] = -1.0
					vcmpdata = vcmpdata + tangentdata.toBytes()
			tanData = NoeBitStream(vcmpdata)
			for i in range(0, meshesSize[2] // 2):
				tanBytes = noesis.encodeFloat16(tanData.readFloat())
				bs.writeUShort(tanBytes)
			for i in range(0, alignedSize[2] - meshesSize[2]):
				bs.writeByte(-1)

		if meshesSize[3] != 0:
			print("Writing colors...")
			vcmpdata = bytearray()
			for mesh in mdl.meshes:
				for vcmp in mesh.colors:
					vcmpdata = vcmpdata + vcmp.toBytes()
			colData = NoeBitStream(vcmpdata)
			for i in range(0, meshesSize[3], 4):
				r, g, b, a = colData.readFloat(), colData.readFloat(), colData.readFloat(), colData.readFloat()
				r, g, b, a = self.floatToColor(r), self.floatToColor(g), self.floatToColor(b), self.floatToColor(a)
				bs.writeUByte(a)
				bs.writeUByte(b)
				bs.writeUByte(g)
				bs.writeUByte(r)
			for i in range(0, alignedSize[3] - meshesSize[3]):
				bs.writeByte(-1)

		if meshesSize[4] != 0:
			print("Writing UVs...")
			for mesh in mdl.meshes:
				for vcmp in mesh.uvs:
					bs.writeUShort(noesis.encodeFloat16(vcmp[0]))
					bs.writeUShort(noesis.encodeFloat16(vcmp[1]))
			for i in range(0, alignedSize[4] - meshesSize[4]):
				bs.writeByte(-1)

		if meshesSize[5] != 0:
			print("Writing blend indices...")
			'''for mesh in mdl.meshes:
				#print(mesh.flatWeightsPerVert)
				if mesh.flatWeightsPerVert != 4:
					#mesh.setFlatWeights(mesh.flatWeightIdx, mesh.flatWeightVal, 4)
					print("DONE")
				for vcmp in mesh.weights:
					for i in range(0, 4):
						if vcmp.numWeights() > i:
							bs.writeUShort(vcmp.indices[i])
						else:
							bs.writeUShort(0)
				pass'''
			for mesh in mdl.meshes:
				for vcmp in mesh.weights:
					for i in range(0, 4):
						if vcmp.numWeights() > i:
							bs.writeUShort(vcmp.indices[i])
						else:
							bs.writeUShort(0)

			for i in range(0, alignedSize[5] - meshesSize[5]):
				bs.writeByte(-1)

		if meshesSize[6] != 0:
			print("Writing blend weights...")
			for mesh in mdl.meshes:
				for vcmp in mesh.weights:
					for i in range(0, 4):
						if vcmp.numWeights() > i:
							bs.writeFloat(vcmp.weights[i])
						else:
							bs.writeFloat(0)

		bs.setEndian(NOE_BIGENDIAN)

		print("Writing face indices...")
		idxCount = 0
		bs.writeInt(1)
		for mesh in mdl.meshes:
			idxCount = idxCount + len(mesh.indices)
		bs.writeInt(idxCount)
		for mesh in mdl.meshes:
			for idx in mesh.indices:
				bs.writeUShort(idx)
		return 1

	def calcPadSize(self, size):
		padding = 0
		while (size % 16) != 0:
			padding += 1
			size += 1
		return size

	def floatToColor(self, f32):
		toColor = 255.0/256
		ret = self.frac(f32 * toColor)
		return int(ret * 256)

	def frac(self, f32):
		return f32 - int(f32)

class psasVitaLoadClass:

	def __init__(self, bs, skel):
		self.bs = bs
		self.skel = skel
		self.texList     = []
		self.matList     = []
		self.matEmis	 = {}
		self.boneList    = []
		self.boneMap     = []
		self.offsetList  = []
		self.meshOffsets = []
		self.meshFvf     = []

	def loadAll(self, bs):
		self.loadModlHeader(bs)
		self.loadFVFInfo(bs)
		self.loadMeshIdx(bs)
		self.loadMatInfo(bs)

	def loadMeshNames(self, bs):
		pass

	def loadBones(self, bs):
		boneMtxList = []
		bp = []
		boneNameList = []

		#print("Loading bones at offset " + str(self.cmdlEnd))
		boneHeader    = bs.read("6I")
		boneMTXOff    = bs.tell() + bs.readUInt()
		boneParOff    = bs.tell() + bs.readUInt()
		boneOff3      = bs.tell() + bs.readUInt()
		boneOff4      = bs.tell() + bs.readUInt()
		boneOff5      = bs.tell() + bs.readUInt()
		boneOff6      = bs.tell() + bs.readUInt()
		boneNameOff   = bs.tell() + bs.readUInt()
		null00, null01, parCount = bs.read("3I")
		for a in range(0,parCount):
			bp.append(bs.read("4B"))
			#print(bp[a])
		#print(boneHeader)
		#print([boneMTXOff, boneParOff, boneOff3, boneOff4, boneOff5, boneOff6, boneNameOff])
		bs.seek(boneMTXOff, NOESEEK_ABS)
		for a in range(0,boneHeader[4]):
			boneRot = NoeQuat.fromBytes(bs.readBytes(16))
			bonePos = NoeVec3.fromBytes(bs.readBytes(12))
			bs.seek(4, NOESEEK_REL)
			boneScale = NoeVec3.fromBytes(bs.readBytes(12))
			bs.seek(4, NOESEEK_REL)
			boneMtx = boneRot.toMat43(1)
			boneMtx[3] = bonePos
			boneMtxList.append(boneMtx)
		bs.seek(boneParOff, NOESEEK_ABS)
		boneParList = bs.read(boneHeader[4] * "H")
		#print(boneParList)
		bs.seek(boneNameOff, NOESEEK_ABS)
		bVer, bStart, bCount, bNull = bs.read("4I")
		bNamebase = bs.tell()
		for a in range(0,bCount):
			bs.seek(bNamebase + (4 * a), NOESEEK_ABS)
			bNameOff = bs.tell() + bs.read("I")[0]
			bs.seek(bNameOff, NOESEEK_ABS)
			boneNameList.append(bs.readString().rsplit('|', 1)[1])
			#print(boneNameList[a])
		for a in range(0,boneHeader[4]):
			newBone = NoeBone(a, boneNameList[a], boneMtxList[a], None, bp[boneParList[a]][2])
			self.boneList.append(newBone)
			#print(self.boneList[a].getMatrix())
		self.boneList = rapi.multiplyBones(self.boneList)

	def loadModlHeader(self, bs):
		self.modlHeader = self.MODLInfo(*( \
		(noeStrFromBytes(bs.readBytes(4)),) \
		+ bs.read(">3I") \
		+ bs.read("I")))
		print(self.modlHeader)

	def loadFVFInfo(self, bs):
		for a in range(0,self.modlHeader.fvfCount):
			fvfHeader = self.FVFInfo(*( \
			(noeStrFromBytes(bs.readBytes(4)),) \
			+ bs.read("2H2I")))
			print(fvfHeader)
			self.meshFvf.append(fvfHeader)

	def loadMeshIdx(self, bs):
		bs.seek(self.modlHeader.modlSize + 0x10, NOESEEK_ABS)
		print(bs.tell())
		idxGroups, idxCount, self.idxBase = bs.read(">2I") + (bs.tell(),)
		print(idxGroups, idxCount, self.idxBase)
		bs.seek(self.idxBase + (2 * idxCount), NOESEEK_ABS)

	def loadBonePallet(self, bs):
		pass

	def loadMatProp(self, bs):
		matHash, propSize = bs.read(">IH")
		return [matHash, propSize]

	def loadDiffuseName(self, bs, material, skip):
		#print("Texture name at: {} with skip: {}".format(bs.getOffset(), skip))
		texNameLength = bs.read("B")[0]
		texPathDifference = skip - texNameLength
		if(texPathDifference > 1):
			texPathDifference -= 1
			bs.seek(texPathDifference, NOESEEK_REL)
		elif(texNameLength == 0):
			print("Diffuse property path is empty, skipping...")
			return 0
		texName = noeStrFromBytes(bs.readBytes(texNameLength))
		texName = rapi.getExtensionlessName(texName.rsplit('/', 1)[1])
		#texName = rapi.getExtensionlessName(texName)
		print(texName)
		material.setTexture(texName)

	def loadNormalName(self, bs, material, skip):
		#print("Texture name at: {} with skip: {}".format(bs.getOffset(), skip))
		texNameLength = bs.read("B")[0]
		texPathDifference = skip - texNameLength
		if(texPathDifference > 1):
			texPathDifference -= 1
			bs.seek(texPathDifference, NOESEEK_REL)
		elif(texNameLength == 0):
			print("Normal property path is empty, skipping...")
			return 0
		texName = noeStrFromBytes(bs.readBytes(texNameLength))
		texName = rapi.getExtensionlessName(texName.rsplit('/', 1)[1])
		#texName = rapi.getExtensionlessName(texName)
		print(texName)
		material.setNormalTexture(texName)

	def loadSpecularName(self, bs, material, skip):
		#print("Texture name at: {} with skip: {}".format(bs.getOffset(), skip))
		texNameLength = bs.read("B")[0]
		texPathDifference = skip - texNameLength
		if(texPathDifference > 1):
			texPathDifference -= 1
			bs.seek(texPathDifference, NOESEEK_REL)
		elif(texNameLength == 0):
			print("Specular property path is empty, skipping...")
			return 0
		texName = noeStrFromBytes(bs.readBytes(texNameLength))
		texName = rapi.getExtensionlessName(texName.rsplit('/', 1)[1])
		#texName = rapi.getExtensionlessName(texName)
		print(texName)
		material.setSpecularTexture(texName)

	def loadEnvironmentName(self, bs, material, skip):
		#print("Texture name at: {} with skip: {}".format(bs.getOffset(), skip))
		texNameLength = bs.read("B")[0]
		texPathDifference = skip - texNameLength
		if(texPathDifference > 1):
			texPathDifference -= 1
			bs.seek(texPathDifference, NOESEEK_REL)
		elif(texNameLength == 0):
			print("Environment property path is empty, skipping...")
			return 0
		texName = noeStrFromBytes(bs.readBytes(texNameLength))
		texName = rapi.getExtensionlessName(texName.rsplit('/', 1)[1])
		#texName = rapi.getExtensionlessName(texName)
		print(texName)
		material.setEnvTexture(texName)

	def loadOpacityName(self, bs, material, skip):
		#print("Texture name at: {} with skip: {}".format(bs.getOffset(), skip))
		texNameLength = bs.read("B")[0]
		texPathDifference = skip - texNameLength
		if(texPathDifference > 1):
			texPathDifference -= 1
			bs.seek(texPathDifference, NOESEEK_REL)
		elif(texNameLength == 0):
			print("Opacity property path is empty, skipping...")
			return 0
		texName = noeStrFromBytes(bs.readBytes(texNameLength))
		texName = rapi.getExtensionlessName(texName.rsplit('/', 1)[1])
		#texName = rapi.getExtensionlessName(texName)
		print(texName)
		material.setOpacityTexture(texName)

	def loadEmissionName(self, bs, material, skip, key):
		texNameLength = bs.read("B")[0]
		texPathDifference = skip - texNameLength
		if(texPathDifference > 1):
			texPathDifference -= 1
			bs.seek(texPathDifference, NOESEEK_REL)
		elif(texNameLength == 0):
			print("Emission property path is empty, skipping...")
			return 0
		texName = noeStrFromBytes(bs.readBytes(texNameLength))
		texName = rapi.getExtensionlessName(texName.rsplit('/', 1)[1])
		#texName = rapi.getExtensionlessName(texName)
		eMat = NoeMaterial(material.name + "_emis", texName)
		#eMat.setBlendMode("GL_SRC_ALPHA", "GL_ONE_MINUS_SRC_ALPHA")
		eMat.setBlendMode("GL_ONE", "GL_ONE")
		eMat.setAlphaTest(0.5)
		self.matEmis[key] = eMat

	def loadMatInfo(self, bs):
		print("Matoffs: " + str(bs.tell()))
		matInfo = []
		matCount = bs.read(">I")[0]
		print(matCount)
		for a in range(0, matCount):
			bs.seek(0x14, NOESEEK_REL)
			matNameSize = bs.read("B")[0]
			matName = "mat_" + str(a) + "_" + noeStrFromBytes(bs.readBytes(matNameSize))
			print(matName)
			material = NoeMaterial(matName, "")
			bs.seek(0x25, NOESEEK_REL)
			matElemCount = bs.read(">H")[0]
			#print(matElemCount)
			for b in range(0, matElemCount):
				matHash, matSkip = self.loadMatProp(bs)
				if matHash in fvfMatLoaderDict:
					fvfMatLoaderDict[matHash](self, bs, material, matSkip)
				elif matHash == 0xE2C837AC: # Handles the emission map
					self.loadEmissionName(bs, material, matSkip, a)
				else:
					#print("Offset: {} | To skip: {} | Buffer size: {}".format(bs.getOffset(), matSkip, bs.getSize()))
					bs.seek(matSkip, NOESEEK_REL)
			bs.seek(0x18, NOESEEK_REL)
			#print(bs.tell())
			self.matList.append(material)
			#if str(fvfTemp[a][4]) in fvfMatLoaderDict:
			#	fvfMatLoaderDict[str()](self, fvfTemp[a], vertBuff)
			#	#print("New fvf Type Found:", fvfTemp[a])
			#else:
			#	pass
				#print("New fvf Type Found:", fvfTemp[a])
		print("Offset mesh: " + str(bs.tell()))
		meshCount = bs.read(">I")[0]
		for a in range(0,meshCount):
			matInfo.append(self.MeshMatInfo(*bs.read(">6fHB4I")))
			#print("Material info: "+ str(matInfo[a]))
		bs.seek(0x4, NOESEEK_REL)
		print(bs.tell())
		self.cmdlEnd = bs.tell()
		#print([self.cmdlEnd ,bs.getSize()])
		self.loadMeshs(bs, matInfo)
		if bs.getSize() > self.cmdlEnd :
			bs.seek(self.cmdlEnd , NOESEEK_ABS)
			if self.skel:
				self.loadBones(bs)

	def loadMeshs(self, bs, matInfo):
		for b in range(0, len(self.meshFvf)):
			print(self.meshFvf[b])
			unit, stride = fvfTypeDict[self.meshFvf[b].fvfType]
			bs.seek(self.meshFvf[b].fvfOffset + 16, NOESEEK_ABS)
			dataBuff = bs.readBytes(self.meshFvf[b].fvfSize)
			print(fvfTypeDict[self.meshFvf[b].fvfType])
			if (self.meshFvf[b].magic == "0SOP"):
				rapi.rpgBindPositionBuffer(dataBuff, unit, stride)
			elif(self.meshFvf[b].magic == "0MRN"):
				rapi.rpgBindNormalBuffer(dataBuff, unit, stride)
			elif(self.meshFvf[b].magic == "0NAT"):
				rapi.rpgBindTangentBuffer(dataBuff, unit, stride)
			elif(self.meshFvf[b].magic == "0LOC"):
				colData = bytearray(dataBuff)
				for x in range(0, (self.meshFvf[b].fvfSize), 4):
					colData[x] = dataBuff[x+3]
					colData[x+1] = dataBuff[x+2]
					colData[x+2] = dataBuff[x+1]
					colData[x+3] = dataBuff[x]
				rapi.rpgBindColorBuffer(colData, unit, stride, 4)
			elif (self.meshFvf[b].magic == "0XET"):
				rapi.rpgBindUV1Buffer(dataBuff, unit, stride)
			elif (self.meshFvf[b].magic == "WNOB"):
				rapi.rpgBindBoneWeightBuffer(dataBuff, unit, stride, 4)
			elif (self.meshFvf[b].magic == "INOB"):
				bs.seek(self.meshFvf[b].fvfOffset + 16, NOESEEK_ABS)
				idxData = []
				for a in range(0, (self.meshFvf[b].fvfSize // 8)):
					f3, f2, f1, f4 = bs.read("4H")
					idxData.append(f1)
					idxData.append(f2)
					idxData.append(f3)
					idxData.append(f4)
				dataBuff = struct.pack("<" + 'H'*len(idxData), *idxData)
				rapi.rpgBindBoneIndexBuffer(dataBuff, unit, stride, 4)

		for a in range(0, len(matInfo)):
			#print(matInfo[a])
			if matInfo[a].matID in self.matEmis.keys():
				self.matList[matInfo[a].matID].setNextPass(self.matEmis[matInfo[a].matID])
			rapi.rpgSetMaterial(self.matList[matInfo[a].matID].name)
			bs.seek(self.idxBase + (2 * matInfo[a].faceStart), NOESEEK_ABS)
			#print("Index of the first face: " + str(bs.tell()))
			faceBuff = rapi.swapEndianArray(bs.readBytes(2 * matInfo[a].faceCount), 2)
			rapi.rpgCommitTriangles(faceBuff, noesis.RPGEODATA_USHORT, matInfo[a].faceCount, noesis.RPGEO_TRIANGLE, 1)


	# MODL information
	MODLInfo = collections.namedtuple('MODLInfo', ' '.join((
		'magic',
		'modlVersion',
		'null00',
		'modlSize',
		'fvfCount'
	)))

	# Mesh Material information
	MeshMatInfo = collections.namedtuple('MeshMatInfo', ' '.join((
		'bbMinX',
		'bbMinY',
		'bbMinZ',
		'bbMaxX',
		'bbMaxY',
		'bbMaxZ',
		'matID',
		'buffID',
		'vertStart',
		'vertCount',
		'faceStart',
		'faceCount'
	)))

	# FVF information
	FVFInfo = collections.namedtuple('FVFInfo', ' '.join((
		'magic',
		'fvfType',
		'fvfVersion',
		'fvfOffset',
		'fvfSize'
	)))


fvfMatLoaderDict = {
	0x73762EDB			: psasVitaLoadClass.loadDiffuseName,
	0xB70C80A5			: psasVitaLoadClass.loadNormalName,
	0xD78D468F			: psasVitaLoadClass.loadSpecularName,
	0x90FB6B27			: psasVitaLoadClass.loadEnvironmentName,
	0xA630DB97			: psasVitaLoadClass.loadOpacityName

	}

fvfTypeDict = {
	1			: (noesis.RPGEODATA_FLOAT, 12), # Positions
	2			: (noesis.RPGEODATA_FLOAT, 16), # Blend weights
	3			: (noesis.RPGEODATA_UBYTE, 4), # Colors
	5			: (noesis.RPGEODATA_HALFFLOAT, 4), # UVs
	6			: (noesis.RPGEODATA_HALFFLOAT, 8), # Normals, tangents
	10			: (noesis.RPGEODATA_USHORT, 8) # Blend indices

	}


class ctxrFile:

	def __init__(self, bs):
		self.bs = bs
		self.texList = []

	def loadAll(self, bs):
		self.loadGXTHeader(bs)
		self.loadGXT(bs)

	def loadGXTHeader(self, bs):
		self.texHeader = self.GXTHeader(*( \
		(noeStrFromBytes(bs.readBytes(4)),) \
		+ bs.read("7I")))
		print(self.texHeader)

	def loadGXT(self, bs):
		texHeader = []

		for a in range(0, self.texHeader.texCount):
			bs.seek(0x20 + (a * 0x20), NOESEEK_ABS)
			texHeader.append(bs.read("5i4B2HI"))
			#print(texHeader[a])
			texName = rapi.getLocalFileName(rapi.getInputName())
			#print(info[a].split(','))
			bs.seek(texHeader[a][0], NOESEEK_ABS)
			texData = bs.readBytes(texHeader[a][1])
			self.psaLoadRGBA(texData, texHeader[a], texName)



	def psaLoadRGBA(self, texData, texInfo, texName):
		#print([texInfo[8], texInfo[9], texInfo[10]])
		#print("I am texture " + texName)

		texFmt = 0
		if texInfo[8] == 0x80:
			#PVRT2BPP
			texFmt = noesis.NOESISTEX_RGBA32
			texData = rapi.imageDecodePVRTC(texData, texInfo[9], texInfo[10], 2, noesis.PVRTC_DECODE_PVRTC2)
		elif texInfo[8] == 0x81:
			#PVRT4BPP
			texFmt = noesis.NOESISTEX_RGBA32
			texData = rapi.imageDecodePVRTC(texData, texInfo[9], texInfo[10], 4, noesis.PVRTC_DECODE_PVRTC2)
		elif texInfo[8] == 0x82:
			#PVRTII2BPP
			texFmt = noesis.NOESISTEX_RGBA32
			texData = rapi.imageDecodePVRTC(texData, texInfo[9], texInfo[10], 2, noesis.PVRTC_DECODE_PVRTC2)
		elif texInfo[8] == 0x83:
			#PVRTII4BPP
			texFmt = noesis.NOESISTEX_RGBA32
			texData = rapi.imageDecodePVRTC(texData, texInfo[9], texInfo[10], 4, noesis.PVRTC_DECODE_PVRTC2)
			texData = rapi.imageDecodeRaw(texData, texInfo[9], texInfo[10], "b8g8r8a8")
		elif texInfo[8] == 0xC:
			#texFmt = noesis.NOESISTEX_DXT1
			texFmt = noesis.NOESISTEX_RGBA32
			#texData = rapi.imageFromMortonOrder(texData, texInfo[9], texInfo[10])
			texData = rapi.imageFromMortonOrder(texData, texInfo[9], texInfo[10], 32 // 8, 2)
			texData = rapi.imageDecodeRaw(texData, texInfo[9], texInfo[10], "b8g8r8a8")
		elif texInfo[8] == 0x0:
			texFmt = noesis.NOESISTEX_RGBA32
			#texData = rapi.imageFromMortonOrder(texData, texInfo[9], texInfo[10])
			texData = rapi.imageFromMortonOrder(texData, texInfo[9]>>1, texInfo[10]>>2, 4)
			texData = rapi.imageDecodeRaw(texData, texInfo[9], texInfo[10], "b8g8r8a8")
		elif texInfo[8] == 0x85:
			#texFmt = noesis.NOESISTEX_DXT1
			texFmt = noesis.NOESISTEX_RGBA32
			texData = rapi.imageFromMortonOrder(texData, texInfo[9]>>1, texInfo[10]>>2, 4)
			texData = rapi.imageDecodeDXT(texData, texInfo[9], texInfo[10], noesis.FOURCC_DXT1)
			texData = rapi.imageDecodeRaw(texData, texInfo[9], texInfo[10], "r8g8b8a8")
		elif texInfo[8] == 0x86:
			#texFmt = noesis.NOESISTEX_DXT3
			texFmt = noesis.NOESISTEX_RGBA32
			texData = rapi.imageFromMortonOrder(texData, texInfo[9]>>1, texInfo[10]>>2, 8)
			texData = rapi.imageDecodeDXT(texData, texInfo[9], texInfo[10], noesis.FOURCC_DXT3)
			texData = rapi.imageDecodeRaw(texData, texInfo[9], texInfo[10], "r8g8b8a8")
		elif texInfo[8] == 0x87:
			#texFmt = noesis.NOESISTEX_DXT5
			texFmt = noesis.NOESISTEX_RGBA32
			texData = rapi.imageFromMortonOrder(texData, texInfo[9]>>1, texInfo[10]>>2, 8)
			texData = rapi.imageDecodeDXT(texData, texInfo[9], texInfo[10], noesis.FOURCC_DXT5)
			texData = rapi.imageDecodeRaw(texData, texInfo[9], texInfo[10], "r8g8b8a8")
		elif texInfo[8] == 0x8B:
			texFmt = noesis.NOESISTEX_RGBA32
			texData = rapi.imageFromMortonOrder(texData, texInfo[9]>>1, texInfo[10]>>2, 8)
			#texData = rapi.imageDecodeDXT(texData, texInfo[9], texInfo[10], noesis.FOURCC_ATI2)
			#texData = rapi.swapEndianArray(texData, 2)
			#texData = rapi.imageDecodePVRTC(texData, texInfo[9], texInfo[10], 4, noesis.PVRTC_DECODE_PVRTC2)
			texData = rapi.imageDecodeRaw(texData, texInfo[9], texInfo[10], "b8g8r8a8")
		elif texInfo[8] == 0x95:
			texFmt = noesis.NOESISTEX_RGBA32
			texData = rapi.imageFromMortonOrder(texData, texInfo[9]>>1, texInfo[10]>>2, 8)
			texData = rapi.imageDecodeRaw(texData, texInfo[9], texInfo[10], "r8g8b8a8")
		elif texInfo[8] == 0x98:
			texFmt = noesis.NOESISTEX_RGBA32
			texData = rapi.imageFromMortonOrder(texData, texInfo[9], texInfo[10], 24 // 8, 2)
			texData = rapi.imageDecodeRaw(texData, texInfo[9], texInfo[10], "b8g8r8")
		#tex1 = NoeTexture(str(texInfo[8]), texInfo[9], texInfo[10], texData, texFmt)
		tex1 = NoeTexture(texName, texInfo[9], texInfo[10], texData, texFmt)
		#print(tex1)
		if texFmt == 0:
			print("ERROR NOT FOUND")
		self.texList.append(tex1)


	# GXT Header
	GXTHeader = collections.namedtuple('GXTHeader', ' '.join((
		'magic',
		'version',
		'texCount',
		'texDataOff',
		'texDataSize',
		'P4Pallet',
		'P8Pallet',
		'pad0'
	)))

def psasVitaWriteMdl(mdl, bs):
	cmdl = psasVitaWriteClass(mdl, bs, False)
	ret = cmdl.psasVitamodWriteModel(cmdl.mdl, cmdl.bs, cmdl.skel)
	return ret

def psasVitaWriteSkn(mdl, bs):
	cmdl = psasVitaWriteClass(mdl, bs, True)
	ret = cmdl.psasVitamodWriteModel(cmdl.mdl, cmdl.bs, cmdl.skel)
	return ret

def psasVitaLoadSkn(data, mdlList):
	ctx = rapi.rpgCreateContext()
	psaVita = psasVitaLoadClass(NoeBitStream(data), True)
	rapi.rpgSetOption(noesis.RPGOPT_TRIWINDBACKWARD, 1)
	rapi.setPreviewOption("autoLoadNonDiffuse", "1")
	#rapi.rpgSetOption(noesis.RPGOPT_BIGENDIAN, 1)
	psaVita.loadAll(psaVita.bs)
	try:
		mdl = rapi.rpgConstructModel()
	except:
		mdl = NoeModel()
	mdl.setModelMaterials(NoeModelMaterials(psaVita.texList, psaVita.matList))
	mdlList.append(mdl); mdl.setBones(psaVita.boneList)
	return 1

def psasVitaLoadMdl(data, mdlList):
	ctx = rapi.rpgCreateContext()
	psaVita = psasVitaLoadClass(NoeBitStream(data), False)
	rapi.rpgSetOption(noesis.RPGOPT_TRIWINDBACKWARD, 1)
	rapi.setPreviewOption("autoLoadNonDiffuse", "1")
	#rapi.rpgSetOption(noesis.RPGOPT_BIGENDIAN, 1)
	psaVita.loadAll(psaVita.bs)
	try:
		mdl = rapi.rpgConstructModel()
	except:
		mdl = NoeModel()
	mdl.setModelMaterials(NoeModelMaterials(psaVita.texList, psaVita.matList))
	mdlList.append(mdl); mdl.setBones(psaVita.boneList)
	return 1

def psaVitatexLoadRGBA(data, texList):
	td = NoeBitStream(data)
	td.seek(0x80, NOESEEK_ABS)
	rapi.setPreviewOption("ddsAti2NoNorm", "0")
	bs = NoeBitStream(td.readBytes(len(data) - 0x80))
	ctxr = ctxrFile(bs)
	ctxr.loadAll(ctxr.bs)
	for a in range(0, len(ctxr.texList)):
		texList.append(ctxr.texList[a])
	return 1
