// North-first, open-boundary BML clearing times using 64-bit row masks.
// The tile is encoded top-to-bottom and anchored at the bottom left.
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

static std::int64_t clearing_time(const std::string& tile, int n) {
    if (tile.size() != 9 || tile.find_first_not_of("13") != std::string::npos || n < 1)
        throw std::runtime_error("expected a fully occupied 3-by-3 tile and positive n");
    const int words = (n + 63) / 64;
    const std::size_t count = std::size_t(n) * words;
    const int remainder = n % 64;
    const std::uint64_t last_mask = remainder ? ((std::uint64_t(1) << remainder) - 1) : ~std::uint64_t(0);
    std::vector<std::uint64_t> east(count, 0), north(count, 0), moving(count, 0);
    for (int row = 0; row < n; ++row) {
        const int tile_row = (row + (3 - n % 3) % 3) % 3;
        for (int col = 0; col < n; ++col) {
            auto& target = tile[tile_row * 3 + col % 3] == '1' ? east : north;
            target[std::size_t(row) * words + col / 64] |= std::uint64_t(1) << (col % 64);
        }
    }
    std::int64_t remaining = std::int64_t(n) * n;
    const std::int64_t budget = 2 * std::int64_t(n) * n * n + 2;
    for (std::int64_t time = 1; time <= budget; ++time) {
        if (time % 2) {
            for (int word = 0; word < words; ++word) {
                moving[word] = north[word];
                remaining -= __builtin_popcountll(moving[word]);
            }
            for (int row = 1; row < n; ++row) {
                const std::size_t offset = std::size_t(row) * words;
                for (int word = 0; word < words; ++word) {
                    const auto idx = offset + word;
                    moving[idx] = north[idx] & ~(east[idx - words] | north[idx - words]);
                }
            }
            for (std::size_t idx = 0; idx < count; ++idx) {
                north[idx] = (north[idx] & ~moving[idx]) | (idx + words < count ? moving[idx + words] : 0);
            }
        } else {
            for (int row = 0; row < n; ++row) {
                const std::size_t offset = std::size_t(row) * words;
                remaining -= (east[offset + words - 1] >> ((n - 1) % 64)) & 1;
                for (int word = 0; word < words; ++word) {
                    const auto idx = offset + word;
                    const auto occupied = east[idx] | north[idx];
                    const auto following = word + 1 < words ? east[idx + 1] | north[idx + 1] : 0;
                    moving[idx] = east[idx] & ~((occupied >> 1) | (following << 63));
                }
                for (int word = 0; word < words; ++word) {
                    const auto idx = offset + word;
                    const auto incoming = word ? moving[idx - 1] >> 63 : 0;
                    east[idx] = (east[idx] & ~moving[idx]) | (moving[idx] << 1) | incoming;
                }
                east[offset + words - 1] &= last_mask;
            }
        }
        if (!remaining) return time;
    }
    throw std::runtime_error("independent cubic budget exceeded");
}

int main(int argc, char** argv) {
    try {
        if (argc < 3) throw std::runtime_error("usage: bitset_survey TILE N [N ...]");
        const std::string tile(argv[1]);
        for (int arg = 2; arg < argc; ++arg) {
            const int n = std::stoi(argv[arg]);
            std::cout << tile << ',' << n << ',' << clearing_time(tile, n) << '\n' << std::flush;
        }
    } catch (const std::exception& exc) {
        std::cerr << exc.what() << '\n';
        return EXIT_FAILURE;
    }
}
