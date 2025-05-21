# src/modern_kata_kupas/utils/alignment.py
"""
Modul utilitas untuk penyelarasan string menggunakan algoritma Needleman-Wunsch.
"""

def align(seq1: str, seq2: str, match_score=1, mismatch_penalty=-1, gap_penalty=-1) -> tuple[str, str, str]:
    """
    Menyelaraskan dua sekuens menggunakan algoritma Needleman-Wunsch.
    
    Args:
        seq1: Sekuens pertama
        seq2: Sekuens kedua
        match_score: Skor untuk kecocokan karakter
        mismatch_penalty: Penalty untuk ketidakcocokan
        gap_penalty: Penalty untuk celah (gap)
        
    Returns:
        Tuple berisi (seq1_aligned, seq2_aligned, alignment_string)
        alignment_string menunjukkan kecocokan ('|'), ketidakcocokan ('.'), atau celah (' ')
    """
    # Inisialisasi matriks
    n, m = len(seq1), len(seq2)
    score_matrix = [[0 for _ in range(m+1)] for _ in range(n+1)]
    
    # Isi baris dan kolom pertama dengan gap penalty
    for i in range(1, n+1):
        score_matrix[i][0] = score_matrix[i-1][0] + gap_penalty
    for j in range(1, m+1):
        score_matrix[0][j] = score_matrix[0][j-1] + gap_penalty
    
    # Isi matriks skor
    for i in range(1, n+1):
        for j in range(1, m+1):
            match = score_matrix[i-1][j-1] + (match_score if seq1[i-1] == seq2[j-1] else mismatch_penalty)
            delete = score_matrix[i-1][j] + gap_penalty
            insert = score_matrix[i][j-1] + gap_penalty
            score_matrix[i][j] = max(match, delete, insert)
    
    # Traceback untuk mendapatkan alignment
    align1, align2 = [], []
    i, j = n, m
    while i > 0 or j > 0:
        if i > 0 and j > 0 and score_matrix[i][j] == score_matrix[i-1][j-1] + \
            (match_score if seq1[i-1] == seq2[j-1] else mismatch_penalty):
            align1.append(seq1[i-1])
            align2.append(seq2[j-1])
            i -= 1
            j -= 1
        elif i > 0 and score_matrix[i][j] == score_matrix[i-1][j] + gap_penalty:
            align1.append(seq1[i-1])
            align2.append('-')
            i -= 1
        else:
            align1.append('-')
            align2.append(seq2[j-1])
            j -= 1
    
    # Balik alignment karena traceback dimulai dari akhir
    align1 = ''.join(reversed(align1))
    align2 = ''.join(reversed(align2))
    
    # Buat string alignment
    alignment_str = []
    for a, b in zip(align1, align2):
        if a == '-' or b == '-':
            alignment_str.append(' ')
        elif a == b:
            alignment_str.append('|')
        else:
            alignment_str.append('.')
    
    return align1, align2, ''.join(alignment_str)