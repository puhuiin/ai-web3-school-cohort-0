最小可用 ERC721 NFT 闭环

1. 写 ERC721 合约
2. 部署合约
3. mint 一枚 NFT
4. 自动生成 tokenId
5. 设置 tokenURI
6. 查询 tokenURI

环境
[Remix IDE]


创建 NFT 合约



1. 新建文件

创建：

```text
MyNFT.sol
```

---

完整最小 ERC721 合约

代码：

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// 引入 OpenZeppelin ERC721
import "@openzeppelin/contracts/token/ERC721/ERC721.sol";

// 用于自动递增 tokenId
import "@openzeppelin/contracts/utils/Counters.sol";

contract MyNFT is ERC721 {

    using Counters for Counters.Counter;
    Counters.Counter private _tokenIds;
    mapping(uint256 => string) private _tokenURIs;
    constructor() ERC721("MyNFT", "MNFT") {}
    function mintNFT(address recipient, string memory uri) public returns (uint256) {
        uint256 newItemId = _tokenIds.current();
        _safeMint(recipient, newItemId);
        _tokenURIs[newItemId] = uri;
        _tokenIds.increment();

        return newItemId;
    }
    function tokenURI(uint256 tokenId)
        public
        view
        override
        returns (string memory)
    {
        return _tokenURIs[tokenId];
    }
}
```



 ERC721

```solidity
import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
```

使用 OpenZeppelin 官方 ERC721 标准实现，不用自己写 NFT 底层逻辑。

部署合约

进入：

```text
Deploy & Run Transactions
```

环境选择：

```text
Remix VM
```

本地测试链

```text
Deploy
```

部署成功后：

```text
Deployed Contracts
```

---

mint 一枚 NFT

展开合约找到：

```text
mintNFT
```

输入：

---

## recipient

测试地址：

```text
当前 account 地址
```

复制 Remix 上面的账户即可

---

## uri

输入：

```text
ipfs://example-metadata
```

点击：

```text
mintNFT
```

成功后：

控制台返回：

```text
0
```

表示：

mint 成功的 tokenId = 0

---

查询 tokenURI

找到：

```text
tokenURI
```

输入：

```text
0
```

点击查询。

会返回：

```text
ipfs://example-metadata
```

官方资料

* [OpenZeppelin ERC721 Docs](https://docs.openzeppelin.com/contracts/5.x/erc721?utm_source=chatgpt.com)
* [Remix IDE](https://remix.ethereum.org?utm_source=chatgpt.com)
* [OpenZeppelin Contracts Github](https://github.com/OpenZeppelin/openzeppelin-contracts?utm_source=chatgpt.com)
