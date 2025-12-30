import { NextRequest, NextResponse } from 'next/server';
import { writeFile, mkdir } from 'fs/promises';
import { join } from 'path';
import { existsSync } from 'fs';

export async function POST(request: NextRequest) {
    try {
        const formData = await request.formData();
        const files = formData.getAll('files') as File[];

        if (!files || files.length === 0) {
            return NextResponse.json(
                { success: false, message: '파일이 없습니다.' },
                { status: 400 }
            );
        }

        // 저장 경로 설정 (프로젝트 루트 기준)
        const saveDir = join(process.cwd(), '..', 'cv.minsol.kr', 'app', 'data', 'yolo');

        // 디렉토리가 없으면 생성
        if (!existsSync(saveDir)) {
            await mkdir(saveDir, { recursive: true });
        }

        const savedFiles: string[] = [];
        const errors: string[] = [];

        for (const file of files) {
            try {
                const bytes = await file.arrayBuffer();
                const buffer = Buffer.from(bytes);

                // 파일명에 타임스탬프 추가하여 중복 방지
                const timestamp = Date.now();
                const originalName = file.name;
                const extension = originalName.split('.').pop();
                const nameWithoutExt = originalName.replace(/\.[^/.]+$/, '');
                const newFileName = `${nameWithoutExt}_${timestamp}.${extension}`;

                const filePath = join(saveDir, newFileName);
                await writeFile(filePath, buffer);
                savedFiles.push(newFileName);
            } catch (error) {
                const errorMessage = error instanceof Error ? error.message : '알 수 없는 오류';
                errors.push(`${file.name}: ${errorMessage}`);
            }
        }

        if (errors.length > 0 && savedFiles.length === 0) {
            return NextResponse.json(
                {
                    success: false,
                    message: '모든 파일 저장 실패',
                    errors
                },
                { status: 500 }
            );
        }

        return NextResponse.json({
            success: true,
            message: `${savedFiles.length}개의 파일이 저장되었습니다.`,
            savedFiles,
            errors: errors.length > 0 ? errors : undefined
        });
    } catch (error) {
        console.error('파일 업로드 오류:', error);
        return NextResponse.json(
            {
                success: false,
                message: '파일 저장 중 오류가 발생했습니다.',
                error: error instanceof Error ? error.message : '알 수 없는 오류'
            },
            { status: 500 }
        );
    }
}

