ped <- ped(
  id = c(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14),
  fid = c(0, 0, 1, 1, 0, 1, 0, 1, 4, 4, 4, 7, 7, 7),
  mid = c(0, 0, 2, 2, 0, 2, 0, 2, 5, 5, 5, 6, 6, 6),
  sex = c(1, 2, 2, 1, 2, 2, 1, 2, 2, 2, 2, 2, 1, 2),
  famid = "",
  reorder = TRUE,
  validate = TRUE,
  detectLoops = TRUE,
  isConnected = FALSE,
  verbose = FALSE
)

# Genotype-specific vectors
carriers <- c(6, 9, 10, 11, 12, 13, 14)
homozygous <- c()
noncarriers <- c(8)
affected <- c(2, 9, 10, 12, 14)
unknown <- c(1, 3, 5)
proband <- 12
