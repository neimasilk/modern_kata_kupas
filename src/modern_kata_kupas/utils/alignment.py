# src/modern_kata_kupas/utils/alignment.py
"""
Modul utilitas untuk penyelarasan string menggunakan algoritma Needleman-Wunsch.
"""

def align(seq1: str, seq2: str, match_score: int = 1, mismatch_penalty: int = -1, gap_penalty: int = -1) -> tuple[str, str, str]:
    """
    Performs global sequence alignment on two strings using the Needleman-Wunsch algorithm.

    This function calculates the optimal alignment between two sequences,
    considering scores for matches, mismatches, and gaps.
    
    Args:
        seq1 (str): The first sequence (string) to align.
        seq2 (str): The second sequence (string) to align.
        match_score (int, optional): The score awarded for matching characters.
                                     Defaults to 1.
        mismatch_penalty (int, optional): The penalty for mismatching characters.
                                          Should be a negative value for penalty.
                                          Defaults to -1.
        gap_penalty (int, optional): The penalty for introducing a gap.
                                     Should be a negative value for penalty.
                                     Defaults to -1.
        
    Returns:
        tuple[str, str, str]: A tuple containing:
            - seq1_aligned (str): The first sequence, padded with '-' for gaps.
            - seq2_aligned (str): The second sequence, padded with '-' for gaps.
            - alignment_string (str): A string indicating the alignment quality:
                - '|' for a match between characters in seq1_aligned and seq2_aligned.
                - '.' for a mismatch.
                - ' ' for a gap (character aligned with '-').
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