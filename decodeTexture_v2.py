import os
import sys


def block_print():
    sys.stdout = open(os.devnull, 'w')


def enable_print():
    sys.stdout = sys.__stdout__


mode = 'c'  # input
outputMode = 'u'  # output

fileDirectory_dict = {  # input
    'a': '.\\Assets\\',
    't': '.\\Test\\',
    'c': '.\\Compressed\\',
    '': '.\\',
}
outputDir_dict = {  # output
    'u': './Uncompressed/',
}
outputDir = outputDir_dict[outputMode]
dir_main = fileDirectory_dict[mode]

fullFileList = []
fileExtList = ('.bin', '.cbin', '.BIN', '.cBin', '.Bin', '.zbin', '.tim2c', '.pzz', '.PZZ')
print(dir_main)
for f_name in os.listdir(dir_main):
    if f_name.endswith(fileExtList):
        fullFileList.append(f_name)

print(fullFileList)
outSecFile = ''
block_print()
curPixelList = []
lifeBarNameLoc = 0
superPortraitLoc = 0
teamIconLoc = 0
pointerList = []
for fileName in fullFileList:
    print(fileName)
    dataSize = os.path.getsize(dir_main + fileName)
    dataRange = dataSize
    # dataRange = 0x00000188
    pointerList = [0, dataRange]
    print(fileName, '0x{0:X} = {0:d} bytes'.format(dataSize))
    inFile = open(dir_main + fileName, 'rb')
    fns = fileName.split('.')
    miniPortraitLoc = ''
    if fileName.endswith(('FAC.BIN', 'fac.bin')):
        print('This is a FAC.BIN')
        lifeBarNameLoc = int.from_bytes(inFile.read(4), 'little')
        superPortraitLoc = int.from_bytes(inFile.read(4), 'little')
        teamIconLoc = int.from_bytes(inFile.read(4), 'little')
        if inFile.tell() != lifeBarNameLoc:
            miniPortraitLoc = int.from_bytes(inFile.read(4), 'little')
        if miniPortraitLoc:
            print(miniPortraitLoc)
            print("Lifebar and Name: 0x%08X\nSuper Portrait:   0x%08X\nTeam Super Icon:  0x%08X"
                  "\nMiniPortrait:  0x%08X" % (
                      lifeBarNameLoc, superPortraitLoc, teamIconLoc, miniPortraitLoc))
            pointerList = [lifeBarNameLoc, superPortraitLoc, teamIconLoc, miniPortraitLoc, dataSize]
        else:
            print("Lifebar and Name: 0x%08X\nSuper Portrait:   0x%08X\nTeam Super Icon:  0x%08X" % (
                lifeBarNameLoc, superPortraitLoc, teamIconLoc))
            pointerList = [lifeBarNameLoc, superPortraitLoc, teamIconLoc, dataSize]
        # miniPortraitLoc = int.from_bytes(inFile.read(4), 'little')
        # spriteLoc = int.from_bytes(inFile.read(4), 'little')

        # pointerList = [lifeBarNameLoc, superPortraitLoc, teamIconLoc, miniPortraitLoc, spriteLoc]

        # breakVal = teamIconLoc
        # inFile.seek(lifeBarNameLoc, 0)

    sectionList = [[] for x in pointerList[0:len(pointerList) - 1]]
    print(len(sectionList))
    for i in range(0, len(pointerList) - 1):
        print('Starting @ Pointer 0x{0:02X}[\'0x{1:08X}\']'.format(i, pointerList[i]),
              'going up to Pointer 0x{0:02X}[\'0x{1:08X}\']'.format(i + 1, pointerList[i + 1]))
        inFile.seek(pointerList[i], 0)
        pSrcImgData = []
        if pointerList[0] > 0:
            nameFSec = fns[0] + '-0x{0:02X}_0x{1:08X}.bin'.format(i, pointerList[i])

            print(' Creating file:', nameFSec)
            outSecFile = open(dir_main + nameFSec, 'wb+')
            fullFileList.append(nameFSec)
        for curCnt in range(pointerList[i], pointerList[i + 1], 2):
            curReadPos = inFile.tell()
            curVal = inFile.read(2)
            if pointerList[0] > 0:
                outSecFile.write(curVal)
            dataPull = '{0:04X}'.format(int.from_bytes(curVal, 'little', signed=False))
            # print('Getting: {0:s} @ [\'0x{1:08X}\']'.format(dataPull, curReadPos))
            pSrcImgData.append(dataPull)

        if pointerList[0] > 0:
            outSecFile.close()
        sectionList[i] = pSrcImgData
        print(len(sectionList[i]))
    if fileName.endswith(('FAC.BIN', 'fac.bin')):
        continue
    inFile.close()
    # exit()
    outFile = open(outputDir + fns[0] + '.decBin', 'wb+')
    for curList in sectionList:
        # enable_print()
        print('Processing data... ')
        # block_print()
        getBitMask = True
        bitMask = 0x0000
        itemCnt = 0x00
        chunk = 0x00
        while itemCnt + 1 <= len(curList):
            value = curList[itemCnt]
            if getBitMask:
                bitMask = int(value, 16)
                print('bitMask: 0x{0:04X} = 0b{0:0>16b} ; Read @ 0x{1:08X}'.format(bitMask, itemCnt * 2))
                getBitMask = False
                itemCnt += 1
                continue
            else:
                # for chunk in range(0, 16):
                curVal = int(curList[itemCnt], 16)
                if bitMask & (0x8000 >> chunk) != 0:  # Compressed
                    if curVal == 0:
                        break
                    print('1 Compressed - 0x%04X ; Read @ 0x%08X' % (curVal, itemCnt * 2))
                    if curVal & 0x07FF == curVal:  # 4-Byte
                        backPixels = curVal
                        if itemCnt > len(curList):
                            print(' itemCnt > len(curList)')
                            exit()
                        grabPixels = int(curList[itemCnt + 1], 16)
                        itemCnt += 2
                        curVal = (curVal << 16) | grabPixels
                        print('  0x{0:08X} :: 4-byte Compressed'.format(curVal))
                        diff = 0
                        if backPixels < grabPixels:
                            diff = grabPixels - backPixels
                            print('grabPixels - backPixels = {0:04X}'.format(diff))
                            grabPixels = backPixels
                            print('  Move 0x%04X pixels back and write 0x%04X times' % (
                                backPixels, grabPixels + diff))
                            # print('  REAL: Move 0x%04X pixels back and write 0x%04X pixels' % (backPixels,
                            #                                                                    grabPixels))
                        else:
                            print('  Move 0x%04X pixels back and grab 0x%04X pixels' % (backPixels, grabPixels))
                        curPos = outFile.tell()
                        grabPos = (curPos - (2 * backPixels))
                        outFile.seek(grabPos, 0)
                        grabbedPixel = []
                        for j in range(0, grabPixels):
                            grabbedPixel.append(int.from_bytes(outFile.read(2), 'little'))
                        print(['0x%04X' % elem for elem in grabbedPixel])
                        print('Length of Grabbed Pixels:', len(grabbedPixel),
                              '; writing these pixels', grabPixels + diff, 'times.')
                        outFile.seek(curPos, 0)
                        for j in range(0, grabPixels + diff):
                            outFile.write(grabbedPixel[j % grabPixels].to_bytes(2, 'little', signed=False))
                    else:  # 2-byte
                        print('  0x%04X :: 2-byte Compressed' % curVal)
                        grabPixels = (curVal & 0xF800) >> 11
                        backPixels = curVal & 0x07FF
                        itemCnt += 1
                        diff = 0
                        print('  Move 0x%02X pixels back and grab 0x%02X pixels.' % (backPixels, grabPixels))
                        if backPixels < grabPixels:
                            diff = grabPixels - backPixels
                            grabPixels = backPixels
                        curPos = outFile.tell()
                        grabPos = (curPos - (2 * backPixels))
                        print(
                            'Current file position: 0x{0:08X} || Grab position: 0x{1:08X}'.format(curPos, grabPos))
                        outFile.seek(grabPos, 0)
                        grabbedPixel = []
                        for j in range(0, grabPixels):
                            grabbedPixel.append(int.from_bytes(outFile.read(2), 'little'))
                        print(['0x%04X' % elem for elem in grabbedPixel])
                        print('0x%04X, 0x%04X, 0x%08X' % (len(grabbedPixel), grabPixels + diff,
                                                          curPos + grabPixels + diff))
                        outFile.seek(curPos, 0)
                        for j in range(0, grabPixels + diff):
                            outFile.write(grabbedPixel[j % grabPixels].to_bytes(2, 'little', signed=False))
                        # print('Currently outFile position is @ {0:08X}'.format(outFile.tell()))
                else:
                    itemCnt += 1
                    # curPixelList.append(curVal)
                    print('0 Uncompressed 0x%04X ; Read @ 0x%08X' % (curVal, itemCnt * 2))
                    outFile.write(curVal.to_bytes(2, 'little', signed=False))
                    # print('Currently outFile position is @ {0:08X}'.format(outFile.tell()))
                chunk += 1
                # print('Currently outFile position is @ {0:08X}'.format(outFile.tell()))
                if chunk == 0x10:
                    chunk = 0x00
                    getBitMask = True
enable_print()
